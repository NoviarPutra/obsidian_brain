---
tags:
  - omniroute/memory
  - omniroute/dashboard
total_memories: 1
last_synced: "2026-09-03T15:21:35.816338+00:00"
---
# 🧠 OmniRoute Knowledge & Memory Hub

Welcome to the automated **OmniRoute Memory Vault**. Memory snapshots from AI sessions are indexed here into specialized memory models.

*Last snapshot taken on 2026-09-03 15:21:35 UTC*

## 📊 Summary by Type

| Memory Category | Record Count | File Link |
| :--- | :--- | :--- |
| **Factual** (Facts, Keys, Specs) | `1` | [[Factual]] |
| **Episodic** (Past Session Experiences) | `0` | [[Episodic]] |
| **Procedural** (Workflows & Rules) | `0` | [[Procedural]] |
| **Semantic** (Conceptual Knowledge) | `0` | [[Semantic]] |

**Total Active Memories**: `1`

---

## 🔍 Dataview Overview

```dataview
TABLE category AS "Category", total_items AS "Total Items", last_synced AS "Last Synced"
FROM #omniroute/memory
WHERE file.name != "Index"
SORT category ASC
```
