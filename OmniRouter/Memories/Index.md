---
tags:
  - omniroute/memory
  - omniroute/dashboard
total_memories: 21
last_synced: "2026-09-26T10:22:13.132304+00:00"
---
# 🧠 OmniRoute Knowledge & Memory Hub

Welcome to the automated **OmniRoute Memory Vault**. Memory snapshots from AI sessions are indexed here into specialized memory models.

*Last snapshot taken on 2026-09-26 10:22:13 UTC*

## 📊 Summary by Type

| Memory Category | Record Count | File Link |
| :--- | :--- | :--- |
| **Factual** (Facts, Keys, Specs) | `12` | [[Factual]] |
| **Episodic** (Past Session Experiences) | `5` | [[Episodic]] |
| **Procedural** (Workflows & Rules) | `3` | [[Procedural]] |
| **Semantic** (Conceptual Knowledge) | `1` | [[Semantic]] |

**Total Active Memories**: `21`

---

## 🔍 Dataview Overview

```dataview
TABLE category AS "Category", total_items AS "Total Items", last_synced AS "Last Synced"
FROM #omniroute/memory
WHERE file.name != "Index"
SORT category ASC
```
