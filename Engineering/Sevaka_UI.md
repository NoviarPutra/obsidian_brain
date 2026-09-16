---
tags:
  - project/sevaka-ui
  - frontend
  - engineering
aliases:
  - sevaka-ui
  - Sevaka UI
title: "Sevaka UI Project Architecture"
---

# 💻 Sevaka UI — HRIS & Enterprise Portal

> **Repository Path**: `/Users/pt-dika/Dika/sevaka-ui`
> **Stack**: React, Vite, TypeScript, Vitest, TailwindCSS
> **Related**: [[Engineering/Index|⚡ Engineering MOC]] | [[Home|🌌 Home]]

---

## 📌 Overview & Scope

Core frontend repository for the enterprise HRIS portal covering employee profile management, attendance, time-off requests, and organization settings.

## 🛠️ Testing & Code Quality Protocol

- Run unit & component tests: `npm run test`
- Always verify Vitest exit codes directly (avoid piping raw through `grep` without `set -o pipefail`).
- Strictly adhere to [[Engineering/Index|Engineering Standards]] and [[Engineering/OmniRoute_Communication_Style|OmniRoute Guidelines]].
