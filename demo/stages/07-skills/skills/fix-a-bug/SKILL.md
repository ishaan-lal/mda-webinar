---
name: fix-a-bug
description: Procedure for fixing a reported bug. Use when existing behavior is wrong, such as wrong text, a broken control, or a scoring error.
---

# Fixing a bug

1. **Get the symptom.** The report must say what happens versus what should
   happen. If it does not, and no attached screenshot shows it, ask for that
   and stop.
2. **Find every occurrence.** `grep -rn` across the repo for the text, key,
   value, or function involved, and read every hit before changing anything.
   In a web app, user-visible text is often written twice: once in the HTML
   markup, and again in the script that updates the page at runtime. Do not
   assume a single occurrence.
3. **Find the cause.** Read enough of the surrounding code to explain *why* it
   happens, not just where. You will need that sentence for the PR. If the
   code already behaves the way the report says it should, say what you
   checked and stop. Do not invent a fix or open a pull request.
4. **Fix the cause.** Make the smallest change that addresses it, in every
   place it lives.
5. **Verify.** Follow *Verifying your change* in your instructions. Re-run the
   same grep from step 2 and show that no wrong occurrence is left.
6. **Note what you learned.** If you have a `/memories/agent/` folder and the
   cause was somewhere a newcomer wouldn't look, add one line about it to
   `/memories/agent/AGENTS.md`.
