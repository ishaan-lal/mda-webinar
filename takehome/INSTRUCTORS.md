# Running the take-home: instructor notes

Before you share the take-home:

1. **Put the Slack invite link** in `README.md` (search for
   `<SLACK INVITE LINK>`).
2. **Let members install apps in the Slack workspace,** or plan to approve
   them. Every student's `mda deploy` installs its own Slack app through
   LangSmith's authorization flow. If the workspace requires admin approval,
   each student is blocked until an admin approves their app. That could be
   dozens of requests right after the webinar.
3. **Expect one bot per student.** The README has each student name theirs
   `Patch-<name>` and DM only their own. Consider a pinned message asking
   people not to @mention other people's bots in shared channels.
4. **Schedules post to each student's own channel** (`#patch-<name>`), so
   there's no shared channel full of roundups. If you'd rather have one shared
   `#patch-roundups`, change the step 10 TODO.
5. **Keep `ishaan-lal/simple-game` public, and keep `main` in its demo-ready
   state** (no planted bug), since students fork it.
6. **LangSmith access:** students need Managed Deep Agents access in a US
   workspace, with a role that can create connections. An RBAC Editor role
   can't, and `mda connections create` returns 403.
7. **Decide what "submitted" means.** The README ends with a "You're done
   when" checklist, but no submission step. Add one if you want, such as a
   shared channel where students post their PR link.
