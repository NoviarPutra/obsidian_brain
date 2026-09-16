---
tags:
  - omniroute/memory
  - omniroute/dashboard
total_memories: 13
last_synced: "2026-09-16T10:23:43.877768+00:00"
---
# 🧠 OmniRoute Knowledge & Memory Hub

Welcome to the automated **OmniRoute Memory Vault**. Memory snapshots from AI sessions are indexed here into specialized memory models.

*Last snapshot taken on 2026-09-16 10:23:43 UTC*

## 📊 Summary by Type

| Memory Category | Record Count | File Link |
| :--- | :--- | :--- |
| **Factual** (Facts, Keys, Specs) | `10` | [[Factual]] |
| **Episodic** (Past Session Experiences) | `1` | [[Episodic]] |
| **Procedural** (Workflows & Rules) | `1` | [[Procedural]] |
| **Semantic** (Conceptual Knowledge) | `1` | [[Semantic]] |

**Total Active Memories**: `13`

---

## 🔍 Dataview Overview

```dataview
TABLE category AS "Category", total_items AS "Total Items", last_synced AS "Last Synced"
FROM #omniroute/memory
WHERE file.name != "Index"
SORT category ASC
```
