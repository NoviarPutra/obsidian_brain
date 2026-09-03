---
tags:
  - worklog/dashboard
  - journal/index
title: "Daily Worklogs & Engineering Journal"
---
# 📓 Daily Worklogs & Engineering Journal

Welcome to your automated daily worklog archive.

---

## 📅 Recent Worklogs

```dataview
TABLE file.mtime AS "Last Modified", tags AS "Tags"
FROM #daily-worklog
SORT file.name DESC
LIMIT 15
```
