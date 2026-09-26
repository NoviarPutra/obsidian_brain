#!/usr/bin/env python3
"""Daily Hermes journal into the Obsidian vault.

The agent never writes the file: this wrapper gathers the facts, asks Hermes for prose
only, and does the writing itself. That is what makes the write target unforgeable —
a prompt injection inside the material being summarised has no tool it can point
anywhere, because the path is computed here from the clock.

Invariants this script is responsible for, in order:
  1. one tick at a time                 (flock, non-blocking)
  2. a day with nothing to report writes no file at all
  3. the entry is capped in size        (a runaway loop cannot write a 50 MB note)
  4. the write is atomic                (temp in the same directory, then os.replace,
                                         so the ~62 s inotify sync never commits half a file)
  5. the vault is never left unlintable (lint after writing; on failure the file is
                                         removed again and the owner is paged)

Failure posture: loud and once. No retry loop, no queue - a queue would be new
unbounded state, which is the bug class this design exists to avoid.

Usage:
  vault-journal.py            write today's entry
  vault-journal.py --dry-run  gather facts and print what would happen, write nothing
"""
import contextlib
import json
import os
import re
import sqlite3
import subprocess
import sys
import tempfile
import urllib.parse
import urllib.request
from datetime import datetime, timedelta, timezone
from pathlib import Path

VAULT = Path("/home/voldemort/services/obsidian-stack/vault")
JOURNAL_DIR = VAULT / "Hermes" / "Journal"
LINT = VAULT / "scripts" / "vault_lint.py"
STATE_DB = Path("/home/voldemort/.hermes/state.db")
HERMES_ENV = Path("/home/voldemort/.hermes/.env")
HERMES_BIN = "/home/voldemort/.local/bin/hermes"
LOCK_PATH = "/tmp/hermes-vault-journal.lock"

WIB = timezone(timedelta(hours=7))
MAX_BODY_CHARS = 6000
HERMES_TIMEOUT_S = 300
LINT_TIMEOUT_S = 120

DRY_RUN = "--dry-run" in sys.argv[1:]


def log(msg):
    print(f"[{datetime.now(WIB).strftime('%Y-%m-%d %H:%M:%S')}] {msg}", flush=True)


# --------------------------------------------------------------- single instance

def acquire_lock():
    """Hold an flock for the process lifetime; a second tick exits instead of racing."""
    import fcntl

    fh = open(LOCK_PATH, "w")
    try:
        fcntl.flock(fh, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except OSError:
        log("another tick holds the lock; exiting")
        sys.exit(0)
    return fh  # returned so it stays open, and thus locked


# --------------------------------------------------------------- fact gathering

def run(cmd, cwd=None, timeout=60):
    p = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, timeout=timeout,
                       stdin=subprocess.DEVNULL)
    return p.returncode, p.stdout.strip(), p.stderr.strip()


def vault_changes():
    """Files touched in the vault in the last 24 h, from git rather than mtimes."""
    rc, out, _ = run(["git", "log", "--since=24 hours ago", "--name-only",
                      "--pretty=format:", "--no-merges"], cwd=str(VAULT))
    if rc != 0:
        return []
    seen, files = set(), []
    for line in out.splitlines():
        line = line.strip()
        if line and line not in seen:
            seen.add(line)
            files.append(line)
    return files


def hermes_activity():
    """Today's own sessions, straight from state.db. Read-only, no locking games."""
    if not STATE_DB.exists():
        return {"sessions": [], "messages": 0, "tool_calls": 0}
    since = datetime.now(WIB).replace(hour=0, minute=0, second=0, microsecond=0)
    # state.db stores timestamps as REAL unix epochs (typeof -> 'real'), so a string
    # comparison here silently matches nothing and every day looks empty.
    since_ts = since.timestamp()
    con = sqlite3.connect(f"file:{STATE_DB}?mode=ro", uri=True, timeout=10)
    try:
        rows = con.execute(
            "SELECT COALESCE(title, session_key), source, message_count, tool_call_count "
            "FROM sessions WHERE COALESCE(last_activity_at, started_at) >= ? "
            "ORDER BY COALESCE(last_activity_at, started_at) DESC LIMIT 20",
            (since_ts,),
        ).fetchall()
        msgs = con.execute("SELECT COUNT(*) FROM messages WHERE timestamp >= ?",
                           (since_ts,)).fetchone()[0]
    except sqlite3.Error as exc:
        log(f"state.db read failed, treating as no activity: {exc}")
        return {"sessions": [], "messages": 0, "tool_calls": 0}
    finally:
        con.close()
    return {
        "sessions": [{"title": r[0], "source": r[1], "messages": r[2], "tools": r[3]} for r in rows],
        "messages": msgs,
        "tool_calls": sum((r[3] or 0) for r in rows),
    }


def gateway_health():
    rc, out, _ = run(["systemctl", "--user", "show", "-p", "ActiveState", "-p", "NRestarts",
                      "--value", "hermes-gateway"])
    return " ".join(out.split()) if rc == 0 else "unknown"


# --------------------------------------------------------------- egress scan

# Everything in `facts` reaches a third-party model, and session titles carry whatever
# the operator typed into Telegram. The hook cannot help here: this payload never passes
# through a tool call, so the scan has to live in the wrapper.
_SECRET_PATTERNS = [
    re.compile(r"\b\d{8,}:[A-Za-z0-9_-]{30,}\b"),                 # telegram bot token
    re.compile(r"\b(?:cfat|cfut|sk|ghp|gho|github_pat)_[A-Za-z0-9_-]{16,}\b"),
    re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----"),
    re.compile(r"\b(?:Bearer|Basic)\s+[A-Za-z0-9._~+/=-]{16,}"),
    re.compile(r"(?i)\b([A-Z0-9_]*(?:TOKEN|SECRET|PASSWORD|APIKEY|API_KEY))\s*[=:]\s*\S{8,}"),
]


def redact(text):
    """Return (redacted_text, hits). Regex, not semantics - it catches known shapes."""
    hits = 0
    for pattern in _SECRET_PATTERNS:
        text, n = pattern.subn("<REDACTED>", text)
        hits += n
    return text, hits


# --------------------------------------------------------------- the prose step

def ask_hermes(facts):
    """Hermes writes prose only. It gets no say in where the result lands."""
    facts_json, hits = redact(json.dumps(facts, ensure_ascii=False, indent=2))
    if hits:
        log(f"egress scan redacted {hits} credential-shaped value(s) before the model call")
    prompt = (
        "Tulis satu entri jurnal harian dalam Bahasa Indonesia formal-lugas, "
        "berdasarkan fakta di bawah. Aturan keras: JANGAN memakai wikilink "
        "[[...]] sama sekali, jangan menulis frontmatter YAML, jangan menulis "
        "judul H1. Mulai langsung dari isi, gunakan heading level 2 ke bawah. "
        "Padat, tanpa basa-basi, maksimal 400 kata. Path, command, dan nama file "
        "tetap dalam bentuk aslinya.\n\n"
        f"FAKTA:\n{facts_json}"
    )
    try:
        p = subprocess.run([HERMES_BIN, "-z", prompt], capture_output=True, text=True,
                           timeout=HERMES_TIMEOUT_S, stdin=subprocess.DEVNULL)
    except subprocess.TimeoutExpired:
        return None, f"hermes -z exceeded {HERMES_TIMEOUT_S}s"
    if p.returncode != 0:
        return None, f"hermes -z exited {p.returncode}: {(p.stderr or p.stdout)[:400]}"
    body = (p.stdout or "").strip()
    if not body:
        return None, "hermes -z returned empty output"
    return body, None


def sanitise(body):
    """Strip what the wrapper owns, and cap the size."""
    body = re.sub(r"\A---\n.*?\n---\n", "", body, flags=re.S)   # any frontmatter it added
    body = re.sub(r"^#\s+.*$", "", body, count=1, flags=re.M)    # any H1 it added
    body = body.strip()
    if len(body) > MAX_BODY_CHARS:
        body = body[:MAX_BODY_CHARS].rstrip() + "\n\n*[dipotong pada batas ukuran entri]*"
    return body


def compose(day, body):
    weekday = ["Senin", "Selasa", "Rabu", "Kamis", "Jumat", "Sabtu", "Minggu"][day.weekday()]
    month = ["Januari", "Februari", "Maret", "April", "Mei", "Juni", "Juli", "Agustus",
             "September", "Oktober", "November", "Desember"][day.month - 1]
    return (
        "---\n"
        "tags:\n"
        "  - hermes/journal\n"
        "  - journal\n"
        f'date: "{day.strftime("%Y-%m-%d")}"\n'
        "---\n\n"
        f"# 🧠 Hermes Journal: {weekday}, {day.day} {month} {day.year}\n\n"
        "> **Related**: [[Worklogs/Index|📓 Worklogs Index]] | "
        "[[Engineering/Hermes_Obsidian_Integration_Spec|🧠 Integration Spec]] | [[Home|🌌 Home]]\n\n"
        f"{body}\n"
    )


# --------------------------------------------------------------- write + verify

def atomic_write(target: Path, text: str):
    """Temp file in the SAME directory, then rename: same filesystem, so the rename is
    atomic and inotify never sees a partially written note."""
    target.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=str(target.parent), prefix=".tmp.journal.")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as fh:
            fh.write(text)
        os.chmod(tmp, 0o644)
        os.replace(tmp, target)
    except BaseException:
        with contextlib.suppress(OSError):
            os.unlink(tmp)
        raise


def lint_ok():
    rc, out, err = run([sys.executable, str(LINT)], cwd=str(VAULT), timeout=LINT_TIMEOUT_S)
    return rc == 0, (out + "\n" + err).strip()


# --------------------------------------------------------------- paging

def page(text):
    """Routine paging goes through Hermes's own bot. The dead-Hermes case is covered by
    the systemd OnFailure unit instead, which does not depend on this process."""
    token = chat = None
    try:
        for line in HERMES_ENV.read_text(encoding="utf-8").splitlines():
            if line.startswith("TELEGRAM_BOT_TOKEN="):
                token = line.split("=", 1)[1].strip()
            elif line.startswith("TELEGRAM_ALLOWED_USERS="):
                chat = line.split("=", 1)[1].split(",")[0].strip()
    except OSError as exc:
        log(f"cannot read {HERMES_ENV} to page: {exc}")
        return
    if not token or not chat:
        log("no telegram token or chat id available; page dropped")
        return
    data = urllib.parse.urlencode({"chat_id": chat, "text": text[:4000]}).encode()
    try:
        with urllib.request.urlopen(
            f"https://api.telegram.org/bot{token}/sendMessage", data=data, timeout=30
        ) as resp:
            resp.read()
        log("owner paged")
    except Exception as exc:  # noqa: BLE001 - paging must never crash the tick
        log(f"paging failed: {exc}")


# --------------------------------------------------------------- main

def main():
    lock = acquire_lock()  # noqa: F841 - must stay referenced for the lock to hold
    day = datetime.now(WIB)
    target = JOURNAL_DIR / f"{day.strftime('%Y-%m-%d')}.md"

    facts = {
        "tanggal": day.strftime("%Y-%m-%d"),
        "vault_files_changed_24h": vault_changes(),
        "hermes_activity_today": hermes_activity(),
        "gateway": gateway_health(),
    }
    activity = facts["hermes_activity_today"]
    nothing_happened = not facts["vault_files_changed_24h"] and not activity["sessions"] \
        and activity["messages"] == 0

    if nothing_happened:
        log("nothing to report today; writing no file (silence is data)")
        return 0

    if DRY_RUN:
        log("dry run; facts follow")
        print(json.dumps(facts, ensure_ascii=False, indent=2))
        log(f"would write {target}")
        return 0

    body, err = ask_hermes(facts)
    if err:
        log(f"ERROR: {err}")
        page(f"🧠 Hermes journal FAILED for {facts['tanggal']}\n\n{err}")
        return 1

    existed = target.exists()
    previous = target.read_text(encoding="utf-8") if existed else None
    atomic_write(target, compose(day, sanitise(body)))
    log(f"wrote {target} ({target.stat().st_size} bytes)")

    ok, detail = lint_ok()
    if ok:
        log("vault lint clean")
        return 0

    # The vault must never be left in a state that blocks every commit for everyone.
    if previous is None:
        target.unlink(missing_ok=True)
        restored = "entry removed"
    else:
        atomic_write(target, previous)
        restored = "previous entry restored"
    log(f"ERROR: vault lint rejected the entry; {restored}")
    log(detail)
    page(
        f"🧠 Hermes journal REVERTED for {facts['tanggal']}\n\n"
        f"vault_lint.py rejected the entry, so it was removed to keep vault sync working "
        f"({restored}).\n\n{detail[:1500]}"
    )
    return 1


if __name__ == "__main__":
    sys.exit(main())
