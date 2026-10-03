---
name: add-a-feature
description: Procedure for adding a small feature. Use when the request asks for new behavior, such as a new control, a button, or a visual change.
---

# Adding a small feature

1. **Get the behavior.** The request must say what the player should be able
   to do and what the result should be. If it does not, ask for that and stop.
2. **Check the scope.** This workflow is for changes of roughly one file and
   under ~100 lines. If the request is bigger than that, needs a new
   dependency, or needs a redesign of existing structure, stop. Say what makes
   it too big and suggest a smaller first step.
3. **Read before writing.** Read the code around where the change goes and
   follow the patterns already there: naming, how existing handlers are
   written, where state is initialized and reset. New code should be hard to
   tell apart from the code around it.
4. **Keep docs in sync.** If the feature adds or changes something a user can
   see or press, grep for where the existing equivalents are documented (a
   README, an on-page help table) and update every one of them.
5. **Implement it.**
6. **Verify.** Follow *Verifying your change* in your instructions.
