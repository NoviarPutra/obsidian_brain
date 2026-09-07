#!/usr/bin/env bash
set -uo pipefail

VAULT_DIR="/Users/pt-dika/Documents/Obsidian"
BRANCH="master"
LOG_FILE="$HOME/Library/Logs/obsidian-sync.log"
LOCK_FILE="/tmp/obsidian_mac_sync.lock"
MAX_LOG_LINES=1000

# 1. Single Instance Protection (shlock / flock alternative for macOS)
mkdir -p "$(dirname "$LOG_FILE")"
exec 200>"$LOCK_FILE"
if ! perl -e 'use Fcntl ":flock"; open(my $fh, ">", $ARGV[0]) or exit 1; flock($fh, LOCK_EX|LOCK_NB) or exit 1;' "$LOCK_FILE"; then
    exit 0
fi

cd "$VAULT_DIR" || exit 1

# 2. Self-Healing: Clean up stale git lockfiles older than 3 minutes
cleanup_stale_locks() {
    local lockfiles
    lockfiles=$(find "$VAULT_DIR/.git" -name "*.lock" -type f -mmin +3 2>/dev/null || true)
    if [[ -n "$lockfiles" ]]; then
        echo "[$(date '+%Y-%m-%d %H:%M:%S')] Found stale git lock files (>3m old). Cleaning up..." >> "$LOG_FILE"
        echo "$lockfiles" | xargs -r rm -f 2>/dev/null || true
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

sync_vault() {
    cleanup_stale_locks
    
    # Check if remote exists
    if ! git remote | grep -q '^origin$'; then
        return
    fi

    # Fetch and rebase remote changes first
    if git fetch origin "$BRANCH" >/dev/null 2>&1; then
        if ! git rebase "origin/$BRANCH" >/dev/null 2>&1; then
            echo "[$(date '+%Y-%m-%d %H:%M:%S')] Rebase conflict detected, aborting rebase..." >> "$LOG_FILE"
            git rebase --abort >/dev/null 2>&1 || true
        fi
    fi

    # Check for local modifications or untracked files
    if [[ -n $(git status --porcelain) ]]; then
        echo "[$(date '+%Y-%m-%d %H:%M:%S')] Local changes detected. Staging and committing..." >> "$LOG_FILE"
        git add -A
        local hostname
        hostname=$(hostname -s 2>/dev/null || echo "Mac")
        local timestamp
        timestamp=$(date -u '+%Y-%m-%dT%H:%M:%SZ')
        git commit -m "Auto-sync by ${hostname} [${timestamp}]" >> "$LOG_FILE" 2>&1 || true
        
        # Push to origin
        if git push origin "$BRANCH" >> "$LOG_FILE" 2>&1; then
            echo "[$(date '+%Y-%m-%d %H:%M:%S')] Vault pushed successfully." >> "$LOG_FILE"
        else
            echo "[$(date '+%Y-%m-%d %H:%M:%S')] Push failed, will retry next cycle." >> "$LOG_FILE"
        fi
    fi

    trim_log
}

sync_vault
