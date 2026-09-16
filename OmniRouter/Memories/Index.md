---
tags:
  - omniroute/memory
  - omniroute/dashboard
total_memories: 14
last_synced: "2026-09-16T11:23:46.966816+00:00"
---
# 🧠 OmniRoute Knowledge & Memory Hub

Welcome to the automated **OmniRoute Memory Vault**. Memory snapshots from AI sessions are indexed here into specialized memory models.

*Last snapshot taken on 2026-09-16 11:23:46 UTC*

## 📊 Summary by Type

| Memory Category | Record Count | File Link |
| :--- | :--- | :--- |
| **Factual** (Facts, Keys, Specs) | `11` | [[Factual]] |
| **Episodic** (Past Session Experiences) | `1` | [[Episodic]] |
| **Procedural** (Workflows & Rules) | `1` | [[Procedural]] |
| **Semantic** (Conceptual Knowledge) | `1` | [[Semantic]] |

**Total Active Memories**: `14`

---

## 🔍 Dataview Overview

```dataview
TABLE category AS "Category", total_items AS "Total Items", last_synced AS "Last Synced"
FROM #omniroute/memory
WHERE file.name != "Index"
SORT category ASC
```
