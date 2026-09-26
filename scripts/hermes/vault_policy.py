#!/usr/bin/env python3
"""pre_tool_call path policy for the Obsidian vault.

Registered as a shell hook on `pre_tool_call` with `fail_closed: true`, so this
script is the only thing standing between a tool call and the vault. It decides by
path, in code, because the alternatives are not guards: the write sandbox
(HERMES_WRITE_SAFE_ROOT) cannot express "this subtree yes, that one no", and prompt
wording cannot bind a model at all.

Contract (agent/shell_hooks.py):
  stdin  {hook_event_name, tool_name, tool_input, session_id, cwd, profile, extra}
  stdout {"action": "block",   "message": str}   -> call denied, message shown to model
         {"action": "approve", "message": str, "rule_key": str} -> human approval gate
         nothing                                 -> call proceeds
  exit 0 always; a crash or unparseable stdout counts as a block because the hook is
  registered fail_closed, which is the direction we want.

Policy, from the approved spec (Engineering/Hermes_Obsidian_Integration_Spec.md):
  Hermes/        writes free            - the agent owns this subtree
  Engineering/   create new only        - editing an existing note escalates to a human
  Worklogs/      writes denied          - sync.sh resolves conflicts with `-X theirs`
                                          and voldemort-menu-bot appends there with no
                                          lock, so this is a data-loss zone
  reads          Engineering/, Worklogs/, Hermes/ only
  anything else inside the vault: denied

Protected paths outside the vault (PROTECTED_ROOTS) are denied outright, for both
file tools and `terminal`. Everything else outside the vault passes through; writes
there are already bounded by HERMES_WRITE_SAFE_ROOT.
"""
import json
import os
import sys

VAULT = "/home/voldemort/services/obsidian-stack/vault"

# Paths outside the vault that Hermes must not touch at all. ~/.omniroute holds
# OmniRoute's storage.sqlite: provider credentials, API keys and combo config. On
# 2026-09-26 an autonomous `terminal` command destroyed it and every OmniRoute route
# answered 500 until the DB was restored from backup. HERMES_WRITE_SAFE_ROOT does not
# cover this path, and `terminal` never consults the write sandbox at all
# (agent/file_safety.py is not imported by tools/terminal_tool.py), so this hook is
# the only place the rule can exist.
PROTECTED_ROOTS = ("/home/voldemort/.omniroute",)

WRITE_FREE = ("Hermes/",)
WRITE_CREATE_ONLY = ("Engineering/",)
WRITE_DENIED = ("Worklogs/",)
READ_ALLOWED = ("Engineering/", "Worklogs/", "Hermes/")

READ_TOOLS = ("read_file", "search_files")
WRITE_TOOLS = ("write_file", "patch")
TERMINAL_TOOLS = ("terminal",)

DIFF_PREVIEW_CHARS = 400


def emit(payload):
    """Single exit point: print the directive (or nothing) and stop."""
    if payload:
        json.dump(payload, sys.stdout)
    sys.exit(0)


def block(message):
    emit({"action": "block", "message": message})


def approve(message, rule_key):
    emit({"action": "approve", "message": message, "rule_key": rule_key})


def under_any(rel, prefixes):
    return any(rel == p.rstrip("/") or rel.startswith(p) for p in prefixes)


def protected_root_for(raw_path, cwd):
    """Return the PROTECTED_ROOTS entry containing raw_path, or None."""
    if not raw_path:
        return None
    path = os.path.expanduser(str(raw_path))
    if not os.path.isabs(path):
        path = os.path.join(cwd or "/", path)
    resolved = os.path.realpath(path)
    for root in PROTECTED_ROOTS:
        real_root = os.path.realpath(root)
        if resolved == real_root or resolved.startswith(real_root + os.sep):
            return root
    return None


def protected_mention(text):
    """Return the protected root a shell string refers to, or None.

    Matched on the directory's own name rather than its full path, because every way
    of writing it - /home/voldemort/.omniroute, ~/.omniroute, $HOME/.omniroute, or a
    `cd` into it followed by a bare filename - contains that token, and a shell string
    cannot be resolved the way a path argument can. A false positive costs one refused
    command; a miss costs the router.
    """
    if not text:
        return None
    for root in PROTECTED_ROOTS:
        if os.path.basename(root) in str(text):
            return root
    return None


def vault_relative(raw_path, cwd):
    """Return the path relative to the vault, or None when it is outside it.

    Resolved with realpath so `../` and symlinks cannot walk out of a prefix that
    only looks correct as a string.
    """
    if not raw_path:
        return None
    path = os.path.expanduser(str(raw_path))
    if not os.path.isabs(path):
        path = os.path.join(cwd or VAULT, path)
    resolved = os.path.realpath(path)
    vault = os.path.realpath(VAULT)
    if resolved == vault:
        return ""
    if not resolved.startswith(vault + os.sep):
        return None
    return resolved[len(vault) + 1:]


def main():
    raw = sys.stdin.read()
    try:
        data = json.loads(raw) if raw.strip() else {}
    except Exception as exc:
        block(f"vault policy hook could not parse its own input ({exc}); denying to fail closed.")

    tool = data.get("tool_name") or ""
    args = data.get("tool_input") or {}
    cwd = data.get("cwd") or VAULT
    if not isinstance(args, dict):
        block("vault policy hook got a non-object tool_input; denying to fail closed.")

    if tool in TERMINAL_TOOLS:
        root = protected_mention(args.get("command")) or protected_mention(args.get("workdir"))
        if root:
            # To let a specific maintenance job through again, swap this block() for
            # approve(msg, f"protected_path:{root}"): that routes the command to a
            # human instead of refusing it, and still fails closed on no answer.
            block(
                f"Command refused: it references {root}, which is off limits. That "
                f"directory holds OmniRoute's storage.sqlite - provider credentials, "
                f"API keys and combo config. A terminal command wiped it on 2026-09-26 "
                f"and every OmniRoute route answered 500 until it was restored from "
                f"backup. Ask the operator to run this themselves."
            )
        emit(None)

    if tool not in READ_TOOLS + WRITE_TOOLS:
        emit(None)

    raw_path = args.get("path")

    protected = protected_root_for(raw_path, cwd)
    if protected:
        block(
            f"Denied: {raw_path!r} is under {protected}. That directory holds "
            f"OmniRoute's storage.sqlite, so Hermes neither reads it - the credentials "
            f"in it would leave this host on the next model call - nor writes it, after "
            f"a terminal command destroyed it on 2026-09-26."
        )

    # search_files without a path would sweep from the cwd, which may be the vault
    # root and would return notes outside the read whitelist.
    if tool == "search_files" and not raw_path:
        block(
            "Pass an explicit `path` to search_files. Vault reads are limited to "
            + ", ".join(READ_ALLOWED)
            + " and an unscoped search cannot be checked against that."
        )

    rel = vault_relative(raw_path, cwd)
    if rel is None:
        emit(None)  # outside the vault: not this policy's concern

    if tool in READ_TOOLS:
        if under_any(rel, READ_ALLOWED):
            emit(None)
        block(
            f"Vault read denied: '{rel}' is outside the allowed read scope "
            f"({', '.join(READ_ALLOWED)}). Vault content leaves this host on every model "
            f"call, so the scope is deliberately narrow. Ask the operator to widen it if "
            f"you need this directory."
        )

    # ---- write tools from here down ----
    if under_any(rel, WRITE_DENIED):
        block(
            f"Vault write denied: '{rel}' is in Worklogs/, which is off limits. That file "
            f"is appended to by voldemort-menu-bot without locking and the vault sync "
            f"script resolves conflicts with `git pull --rebase -X theirs`, so a write "
            f"here can be silently discarded or committed with conflict markers. Write to "
            f"Hermes/ instead."
        )

    if under_any(rel, WRITE_FREE):
        emit(None)

    if under_any(rel, WRITE_CREATE_ONLY):
        target = os.path.join(os.path.realpath(VAULT), rel)
        if not os.path.exists(target):
            emit(None)  # creating a new note is allowed
        detail = ""
        if tool == "patch":
            old = str(args.get("old_string") or "")[:DIFF_PREVIEW_CHARS]
            new = str(args.get("new_string") or "")[:DIFF_PREVIEW_CHARS]
            detail = f"\n--- replacing ---\n{old}\n+++ with +++\n{new}"
        else:
            body = str(args.get("content") or "")
            detail = (
                f"\n--- whole-file overwrite, {len(body)} chars, first "
                f"{DIFF_PREVIEW_CHARS} ---\n{body[:DIFF_PREVIEW_CHARS]}"
            )
        approve(
            f"Edit an EXISTING human-authored note: {rel}{detail}",
            f"vault_edit:{rel}",
        )

    block(
        f"Vault write denied: '{rel}' is not in a writable area. Hermes may write freely "
        f"under Hermes/, may create new notes under Engineering/, and nowhere else."
    )


if __name__ == "__main__":
    main()
