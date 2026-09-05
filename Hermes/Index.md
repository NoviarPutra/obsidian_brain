---
tags:
  - hermes/agent
  - hermes/dashboard
total_sessions: 2
last_synced: "2026-09-05T06:13:27.808247+00:00"
---
# ⚕️ Hermes Agent Knowledge & Session Archive

*Synced from local Hermes database on 2026-09-05 06:13:27 UTC*

## 🛠️ Integrated Capabilities

- **Obsidian MCP Server**: `Enabled` (14 file & vault tools)
- **Primary Model**: `AG` (Gemini 3.7 Flash High via OmniRoute Gateway)
- **Recorded CLI Sessions**: `2`

---

## 📜 Recent Agent Sessions

| Title / Session | Model | Working Dir | Messages | Started At |
| :--- | :--- | :--- | :--- | :--- |
| **`Generate cinematic Lord Voldemort portrait`** | `AG` | `/home/budiawan` | `6` | `2026-09-05 06:12` |
| **`Generate neon cybernetic owl image`** | `AG` | `/home/budiawan` | `6` | `2026-09-05 06:09` |

---

## 🔍 Dataview Query

```dataview
TABLE model AS "Model", cwd AS "Working Directory", message_count AS "Messages"
FROM #hermes/session
SORT started_at DESC
```
