---
tags:
  - omniroute/memory
  - omniroute/memory/procedural
category: "Procedural"
total_items: 2
last_synced: "2026-09-25T01:48:30.036647+00:00"
---
# 🧠 OmniRoute Memory: Procedural

*Synced from OmniRoute VPS database on 2026-09-25 01:48:30 UTC*

**Total `Procedural` Records**: `2`

## 📌 `preference:image_generation_workflow`

- **Key**: `preference:image_generation_workflow`
- **Access Count**: `8`
- **Created**: `2026-09-25T01:29:57.800Z`
- **Updated**: `2026-09-25T01:29:57.800Z`

### Memory Content
```text
Workflow preference: When user shares creative/image ideas, brainstorm/engineer prompt and invoke Hermes CLI directly for image generation unless user asks specifically for prompt recipes only.
```

### Metadata
```json
{
  "reason": "User context outlines end-to-end autonomous visual workflow using Hermes CLI"
}
```

---

## 📌 `user_image_prompting_workflow`

- **Key**: `user_image_prompting_workflow`
- **Access Count**: `21203`
- **Created**: `2026-09-06T18:17:21.731Z`
- **Updated**: `2026-09-06T18:18:46.269Z`

### Memory Content
```text
End-to-end visual workflow: User shares creative/image idea, Kilo brainstorms/refines and engineers the anti-AI-slop optical prompt, then Kilo directly invokes Hermes CLI (hermes -z / Cloudflare FLUX image_gen) to produce the final image artifact without requiring manual copy-paste from user. If user explicitly asks only for prompt recipes, provide prompts. Otherwise execute end-to-end autonomously.
```

### Metadata
```json
{
  "reason": "Update memory to support seamless autonomous end-to-end image generation via Hermes"
}
```

---
