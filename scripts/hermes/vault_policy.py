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

Paths outside the vault are not this hook's business and pass through; writes there
are already bounded by HERMES_WRITE_SAFE_ROOT.
"""
import json
import os
import sys

VAULT = "/home/voldemort/services/obsidian-stack/vault"

WRITE_FREE = ("Hermes/",)
WRITE_CREATE_ONLY = ("Engineering/",)
WRITE_DENIED = ("Worklogs/",)
READ_ALLOWED = ("Engineering/", "Worklogs/", "Hermes/")

READ_TOOLS = ("read_file", "search_files")
WRITE_TOOLS = ("write_file", "patch")

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

    if tool not in READ_TOOLS + WRITE_TOOLS:
        emit(None)

    raw_path = args.get("path")

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
