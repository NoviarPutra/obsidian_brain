#!/usr/bin/env bash
# OnFailure target for hermes-journal.service.
#
# Deliberately pages through the MENU bot token, not Hermes's own: this unit exists for
# the cases where Hermes is the thing that broke (OOM-killed by MemoryMax, unit failed to
# start, wrapper timed out), and a dead agent cannot report its own death.
set -uo pipefail

ENV_FILE=/home/voldemort/services/telegram-bot/.env
CHAT_ID=708066102
UNIT="${1:-hermes-journal.service}"

TOKEN="$(sed -n 's/^BOT_TOKEN=//p' "$ENV_FILE" | head -1)"
[ -n "$TOKEN" ] || { echo "no BOT_TOKEN in $ENV_FILE"; exit 1; }

STATUS="$(systemctl --user show -p Result -p ExecMainStatus -p ActiveState --value "$UNIT" 2>/dev/null | paste -sd' ')"
TAIL="$(journalctl --user -u "$UNIT" -n 12 --no-pager 2>/dev/null | tail -12)"

TEXT="$(printf '🚨 %s FAILED\n\nresult/status/state: %s\n\nlast log lines:\n%s' "$UNIT" "$STATUS" "$TAIL")"

curl -sS --max-time 30 -o /dev/null \
    --data-urlencode "chat_id=${CHAT_ID}" \
    --data-urlencode "text=${TEXT:0:3900}" \
    "https://api.telegram.org/bot${TOKEN}/sendMessage" \
  && echo "alert sent" || echo "alert delivery failed"
