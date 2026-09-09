---
tags:
  - hermes/agent
  - hermes/dashboard
total_sessions: 9
last_synced: "2026-09-09T17:19:30.343231+00:00"
---
# ⚕️ Hermes Agent Knowledge & Session Archive

*Synced from local Hermes database on 2026-09-09 17:19:30 UTC*

## 🛠️ Integrated Capabilities

- **Obsidian MCP Server**: `Enabled` (14 file & vault tools)
- **Primary Model**: `AG` (Gemini 3.7 Flash High via OmniRoute Gateway)
- **Recorded CLI Sessions**: `9`

---

## 📜 Recent Agent Sessions

| Title / Session | Model | Working Dir | Messages | Started At |
| :--- | :--- | :--- | :--- | :--- |
| **`Inspect Home.md first line`** | `AG` | `/home/budiawan` | `5` | `2026-09-09 17:19` |
| **`reply with exactly: HERMES_OK`** | `AG` | `/home/budiawan` | `2` | `2026-09-09 17:18` |
| **`test ping`** | `AG` | `/home/budiawan` | `1` | `2026-09-09 17:16` |
| **`Generate brass rotary dial image`** | `AG` | `/home/budiawan` | `8` | `2026-09-06 18:14` |
| **`Generate Swiss API Gateway poster SVG`** | `AG` | `/home/budiawan` | `10` | `2026-09-06 18:01` |
| **`Daftar provider fitur free tier`** | `AG` | `/home/budiawan` | `4` | `2026-09-05 20:03` |
| **`Ringkasan perkembangan AI tahun 2026`** | `AG` | `/home/budiawan` | `6` | `2026-09-05 20:01` |
| **`Generate cinematic Lord Voldemort portrait`** | `AG` | `/home/budiawan` | `6` | `2026-09-05 06:12` |
| **`Generate neon cybernetic owl image`** | `AG` | `/home/budiawan` | `6` | `2026-09-05 06:09` |

---

## 🔍 Dataview Query

```dataview
TABLE model AS "Model", cwd AS "Working Directory", message_count AS "Messages"
FROM #hermes/session
SORT started_at DESC
```
