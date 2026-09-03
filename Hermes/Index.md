---
tags:
  - hermes/agent
  - hermes/dashboard
total_sessions: 0
last_synced: "2026-09-03T14:46:52.459342+00:00"
---
# ⚕️ Hermes Agent Knowledge & Session Archive

*Synced from local Hermes database on 2026-09-03 14:46:52 UTC*

## 🛠️ Integrated Capabilities

- **Obsidian MCP Server**: `Enabled` (14 file & vault tools)
- **Primary Model**: `AG` (Gemini 3.7 Flash High via OmniRoute Gateway)
- **Recorded CLI Sessions**: `0`

---

## 📜 Recent Agent Sessions

| Title / Session | Model | Working Dir | Messages | Started At |
| :--- | :--- | :--- | :--- | :--- |
| *(No sessions recorded yet)* | - | - | - | - |

> [!NOTE]
> Hermes sessions will automatically appear here once conversations are completed in CLI.

---

## 🔍 Dataview Query

```dataview
TABLE model AS "Model", cwd AS "Working Directory", message_count AS "Messages"
FROM #hermes/session
SORT started_at DESC
```
