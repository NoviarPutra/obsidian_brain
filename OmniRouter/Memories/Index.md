---
tags:
  - omniroute/memory
  - omniroute/dashboard
total_memories: 22
last_synced: "2026-09-24T10:33:08.048495+00:00"
---
# 🧠 OmniRoute Knowledge & Memory Hub

Welcome to the automated **OmniRoute Memory Vault**. Memory snapshots from AI sessions are indexed here into specialized memory models.

*Last snapshot taken on 2026-09-24 10:33:08 UTC*

## 📊 Summary by Type

| Memory Category | Record Count | File Link |
| :--- | :--- | :--- |
| **Factual** (Facts, Keys, Specs) | `13` | [[Factual]] |
| **Episodic** (Past Session Experiences) | `3` | [[Episodic]] |
| **Procedural** (Workflows & Rules) | `5` | [[Procedural]] |
| **Semantic** (Conceptual Knowledge) | `1` | [[Semantic]] |

**Total Active Memories**: `22`

---

## 🔍 Dataview Overview

```dataview
TABLE category AS "Category", total_items AS "Total Items", last_synced AS "Last Synced"
FROM #omniroute/memory
WHERE file.name != "Index"
SORT category ASC
```
