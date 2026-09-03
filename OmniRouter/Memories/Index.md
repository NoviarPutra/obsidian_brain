---
tags:
  - omniroute/memory
  - omniroute/dashboard
total_memories: 0
last_synced: "2026-09-03T14:25:14.425955+00:00"
---
# 🧠 OmniRoute Knowledge & Memory Hub

Welcome to the automated **OmniRoute Memory Vault**. Memory snapshots from AI sessions are indexed here into specialized memory models.

*Last snapshot taken on 2026-09-03 14:25:14 UTC*

## 📊 Summary by Type

| Memory Category | Record Count | File Link |
| :--- | :--- | :--- |
| **Factual** (Facts, Keys, Specs) | `0` | [[Factual]] |
| **Episodic** (Past Session Experiences) | `0` | [[Episodic]] |
| **Procedural** (Workflows & Rules) | `0` | [[Procedural]] |
| **Semantic** (Conceptual Knowledge) | `0` | [[Semantic]] |

**Total Active Memories**: `0`

---

## 🔍 Dataview Overview

```dataview
TABLE category AS "Category", total_items AS "Total Items", last_synced AS "Last Synced"
FROM #omniroute/memory
WHERE file.name != "Index"
SORT category ASC
```
