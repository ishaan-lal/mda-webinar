---
name: open-a-pull-request
description: How to open a pull request with the GitHub tools, what it must contain, and how to handle follow-up changes. Use after a change is made and verified.
---

# Opening the pull request

1. Run `git -C /workspace/app status --short` and make sure every path listed
   is one you meant to change. Revert anything else.
2. If you have `/memories/user/AGENTS.md`, check it. If this person prefers
   drafts, set `draft: true` on the pull request.
3. Follow *Opening a pull request* under *Tools* in your instructions:
   create the branch, push every changed file in one commit, then open the
   pull request with the title and body below.

A human approves the pull request before it is created. If they reject it, say
so in one line, mention that the branch was left in place, and don't try again
unless asked.

## Follow-ups

If you already opened a pull request in this conversation and the person asks
for more changes, **don't open another one**. Make the change, then
`github__push_files` the changed files to **the same branch**. That adds a
commit to the existing pull request. Reply with the same PR link.

For unrelated work, suggest starting a new conversation.

## Title

`Fix: <what was wrong>` or `Feat: <what it adds>`, under 60 characters.

## Body

```markdown
## What
<For a fix: the symptom. For a feature: what it does and how it behaves.>

## Why
<For a fix: the root cause. For a feature: decisions you made that the request
left open.>

## Changes
- `<file>`: <what changed>

## Verified
- <each check you ran and what it showed>

Opened by Patch, a Managed Deep Agent.
```

If a GitHub tool returns an error, report it in your reply. Do not fall back
to git.
