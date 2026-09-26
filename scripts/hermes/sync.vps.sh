#!/usr/bin/env bash
set -uo pipefail

VAULT_DIR="${VAULT_DIR:-/app/vault}"
BRANCH="${BRANCH:-master}"
LOG_FILE="${LOG_DIR:-/app/logs}/sync.log"
LOCK_FILE="/tmp/obsidian_vps_sync.lock"
MAX_LOG_LINES=1000

log() {
    local msg="[$(date '+%Y-%m-%d %H:%M:%S')] $*"
    echo "$msg"
    if [[ -d "$(dirname "$LOG_FILE")" ]]; then
        echo "$msg" >> "$LOG_FILE" 2>/dev/null || true
    fi
}

# 1. Single Instance Protection (Flock)
exec 200>"$LOCK_FILE"
if ! flock -n 200; then
    log "Another instance of Obsidian sync is already running. Exiting."
    exit 0
fi

cd "$VAULT_DIR" || {
    log "Error: Vault directory $VAULT_DIR does not exist!"
    exit 1
}

# 2. Self-Healing: Clean up stale git lockfiles older than 3 minutes
cleanup_stale_locks() {
    local lockfiles
    lockfiles=$(find "$VAULT_DIR/.git" -name "*.lock" -type f -mmin +3 2>/dev/null || true)
    if [[ -n "$lockfiles" ]]; then
        log "Found stale git lock files (>3m old): $lockfiles. Cleaning up..."
        echo "$lockfiles" | xargs -r rm -f
    fi
}

# 3. Log Truncation
trim_log() {
    if [[ -f "$LOG_FILE" ]]; then
        local line_count
        line_count=$(wc -l < "$LOG_FILE" 2>/dev/null || echo 0)
        if (( line_count > MAX_LOG_LINES )); then
            tail -n "$MAX_LOG_LINES" "$LOG_FILE" > "${LOG_FILE}.tmp" && mv "${LOG_FILE}.tmp" "$LOG_FILE"
        fi
    fi
}

has_remote() {
    git remote | grep -q '^origin$'
}

sync_up() {
    cleanup_stale_locks
    if [[ -n $(git status --porcelain) ]]; then
        log "Changes detected. Committing..."
        git add -A
        # A rejected commit must not be swallowed. With || true the failure vanished
        # and the push right after it ran anyway, so a blocked commit looked normal.
        if git commit -m "Auto-sync by OmniRouter [$(date -u +'%Y-%m-%dT%H:%M:%SZ')]" 2>&1; then
            if has_remote; then
                log "Pushing to origin/$BRANCH..."
                git push origin "$BRANCH" 2>&1 || log "Warning: git push deferred."
            fi
        else
            log "ERROR: git commit REJECTED (pre-commit hook or git failure). NOT pushing; tree stays dirty. Diagnose with: python3 $VAULT_DIR/scripts/vault_lint.py"
        fi
    fi
}

sync_down() {
    cleanup_stale_locks
    if has_remote; then
        if [[ -n $(git status --porcelain) ]]; then
            sync_up
        fi
        log "Fetching and rebasing from origin/$BRANCH..."
        if ! git fetch origin "$BRANCH" 2>&1; then
            log "Warning: git fetch failed (network offline or SSH issue). Will retry next cycle."
            return
        fi
        if ! git rebase "origin/$BRANCH" 2>&1; then
            log "Rebase conflict encountered. Resolving with remote priority for user notes..."
            git rebase --abort 2>/dev/null || true
            git stash 2>/dev/null || true
            git pull --rebase -X theirs origin "$BRANCH" 2>&1 || {
                log "Fallback: clean pull..."
                git rebase --abort 2>/dev/null || true
                git pull origin "$BRANCH" 2>&1 || true
            }
            git stash pop 2>/dev/null || true
        fi
    fi
}

log "Starting Bullet-Proof Obsidian Sync Daemon for $VAULT_DIR..."
sync_up
sync_down

GC_COUNTER=0
while true; do
    # Wait for file changes OR timeout after 60s to pull remote changes
    inotifywait -t 60 -r -e modify,create,delete,move --exclude '\.git' "$VAULT_DIR" 2>/dev/null || true
    sleep 2
    sync_up
    sync_down
    trim_log
    # Periodic git garbage collection
    GC_COUNTER=$((GC_COUNTER + 1))
    if [ "$GC_COUNTER" -ge 60 ]; then
        git gc --auto --quiet 2>/dev/null || true
        GC_COUNTER=0
    fi
done
