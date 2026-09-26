#!/usr/bin/env bash
# OnFailure target for hermes-journal.service.
#
# Deliberately pages through the MENU bot token, not Hermes's own: this unit exists for
# the cases where Hermes is the thing that broke (OOM-killed by MemoryMax, unit failed to
# start, wrapper timed out), and a dead agent cannot report its own death.
set -uo pipefail

ENV_FILE=/home/voldemort/services/telegram-bot/.env
CHAT_ID=708066102

# --dry-run prints the message instead of sending it, so this path can be tested without
# putting a scary alert in the owner's DM.
DRY_RUN=0
ARGS=()
for a in "$@"; do
    case "$a" in
        --dry-run) DRY_RUN=1 ;;
        *) ARGS+=("$a") ;;
    esac
done
UNIT="${ARGS[0]:-hermes-journal.service}"

TOKEN="$(sed -n 's/^BOT_TOKEN=//p' "$ENV_FILE" | head -1)"
[ -n "$TOKEN" ] || { echo "no BOT_TOKEN in $ENV_FILE"; exit 1; }

RESULT="$(systemctl --user show -p Result --value "$UNIT" 2>/dev/null || echo unknown)"
STATUS="$(systemctl --user show -p Result -p ExecMainStatus -p ActiveState --value "$UNIT" 2>/dev/null | paste -sd' ')"
TAIL="$(journalctl --user -u "$UNIT" -n 12 --no-pager 2>/dev/null | tail -12)"

# The header used to be hardcoded to FAILED, so a manual run of this script cried wolf
# with the unit sitting at Result=success. An alert that cannot tell failure from success
# teaches the owner to ignore it, which costs exactly the one alert that matters.
if [ "$RESULT" = "success" ]; then
    HEADER="$(printf 'ℹ️ %s did NOT fail (Result=success)\n\nThis message came from a manual or test run of journal-alert.sh, not from systemd OnFailure. No action needed.' "$UNIT")"
else
    HEADER="$(printf '🚨 %s FAILED' "$UNIT")"
fi

TEXT="$(printf '%s\n\nresult/status/state: %s\n\nlast log lines:\n%s' "$HEADER" "$STATUS" "$TAIL")"

if [ "$DRY_RUN" = 1 ]; then printf '%s\n' "$TEXT"; exit 0; fi

curl -sS --max-time 30 -o /dev/null \
    --data-urlencode "chat_id=${CHAT_ID}" \
    --data-urlencode "text=${TEXT:0:3900}" \
    "https://api.telegram.org/bot${TOKEN}/sendMessage" \
  && echo "alert sent" || echo "alert delivery failed"
