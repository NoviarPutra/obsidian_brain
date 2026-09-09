---
tags:
  - hermes/agent
  - hermes/dashboard
total_sessions: 7
last_synced: "2026-09-09T17:17:12.674568+00:00"
---
# ⚕️ Hermes Agent Knowledge & Session Archive

*Synced from local Hermes database on 2026-09-09 17:17:12 UTC*

## 🛠️ Integrated Capabilities

- **Obsidian MCP Server**: `Enabled` (14 file & vault tools)
- **Primary Model**: `AG` (Gemini 3.7 Flash High via OmniRoute Gateway)
- **Recorded CLI Sessions**: `7`

---

## 📜 Recent Agent Sessions

| Title / Session | Model | Working Dir | Messages | Started At |
| :--- | :--- | :--- | :--- | :--- |
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
