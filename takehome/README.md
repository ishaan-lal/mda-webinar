# Managed Deep Agents Take-home: Build your own Patch

In the webinar you watched **Patch** get built: a Managed Deep Agent (MDA) that
lives in Slack, fixes bugs in a small browser game, and opens pull requests,
asking a human to approve first. Now you build your own. It works on **your
fork** of the game and lives in the webinar's Slack workspace.

You build it the same way as the demo, one feature at a time:

- [`my-agent/`](my-agent/) is your project. It starts as a bare agent, and it
  runs as-is.
- [`add-ons/`](add-ons/) has one folder per step. Each step, you copy that
  folder's files into `my-agent/`, then fill in the `TODO`s.
- [`solution/`](solution/) is the finished agent. Try each step yourself first,
  then compare.

In MDA, a file's **location** turns a feature on. Adding `sandbox/` gives the
agent a computer, and adding `memory.py` gives it memory. That's why you copy
the pieces in one at a time instead of starting with all of them.

For anything not covered here, see the
[Managed Deep Agents docs](https://docs.langchain.com/langsmith/python/managed-deep-agents-overview).

---

## What you need

- A **LangSmith** account (US region) with Managed Deep Agents access, plus an
  API key and your workspace ID. Use a workspace where you're an admin: step 9
  creates a *connection*, which some roles can't do.
- An **Anthropic API key**
- [**uv**](https://docs.astral.sh/uv/getting-started/installation/)
- A **GitHub** account
- An account in the webinar **Slack workspace**: `<SLACK INVITE LINK>`

---

## Setup

1. **Fork the game.** Fork
   [`ishaan-lal/simple-game`](https://github.com/ishaan-lal/simple-game) to
   your GitHub account. Patch only ever works on your fork.
2. **Make a GitHub token for your fork only.** In GitHub, go to *Settings →
   Developer settings → Fine-grained tokens → Generate new token*:
   - *Repository access:* **Only select repositories** → your fork
   - *Permissions:* **Contents** read and write, and **Pull requests** read and
     write

   The token's scope is Patch's real guardrail: it physically can't touch any
   other repo.
3. **Fill in `.env`.**
   ```bash
   cd my-agent
   uv sync
   cp .env.example .env
   ```
   Fill in `LANGSMITH_API_KEY`, `LANGSMITH_WORKSPACE_ID`, `ANTHROPIC_API_KEY`,
   `PATCH_REPO` (your fork, like `octocat/simple-game`), and
   `MDA_DEV_PATCH_GITHUB` (the token).

---

## How each step works

Keep two terminals open: one in `takehome/` for copying, and one in
`takehome/my-agent/` for `uv run mda dev`.

1. **Copy** the step's add-on files into `my-agent/` (each step gives the
   commands).
2. **Fill in the `TODO`s.** Every one is marked `TODO(step N)` and explains
   what to write. To see what's left:
   ```bash
   grep -rn "TODO" my-agent --exclude-dir=.venv --exclude-dir=.mda
   ```
3. **Restart `mda dev`** (`Ctrl+C`, then `uv run mda dev`). New files are only
   picked up when it starts.
4. **Run the checkpoint** query in Studio and check the trace. Start a **new
   thread** for each step, so earlier conversations don't get in the way.

Stuck? The finished file for every step is in `solution/`.

---

## Step 1: Run the bare agent

**TODO:** in `my-agent/agent.py`, give your agent a `name`.

```bash
uv run mda dev
```

**Checkpoint:**

> What's in your workspace? And what versions of git and Node can you run?

It has file tools, but no machine to run anything on. Remember this answer.

---

## Step 2: Give it a computer (sandbox)

```bash
cp -R add-ons/02-sandbox/sandbox my-agent/sandbox
```

Nothing to write. Skim the two files:

- `sandbox/__init__.py` declares the sandbox. The folder's presence is what
  turns it on: every conversation (thread) now gets its own isolated machine.
- `sandbox/setup.sh` runs **once**, when the sandbox snapshot is built, not on
  every conversation. It installs only tooling (git and Node), and every new
  thread starts from that snapshot.

**Checkpoint:** restart `mda dev` (the first snapshot build can take a few
minutes), then send the **same** query as step 1. This time it runs real
commands.

---

## Step 3: Get your fork into the sandbox (middleware)

```bash
cp add-ons/03-checkout/config.py my-agent/
cp -R add-ons/03-checkout/middleware my-agent/
```

Skim the two files:

- `config.py` is the only place in the project that names the repo. It reads
  `PATCH_REPO` from `.env`.
- `middleware/checkout.py` clones your fork into the sandbox before the model
  runs, once per thread. Cloning is plumbing, not judgment, so it's code
  rather than a line in the prompt asking the model to do it. `runtime.backend`
  is the thread's sandbox, which MDA adds for you.

**TODO (wiring):** unlike a sandbox, middleware is code, so `agent.py` has to
import it. Add:

```python
from middleware.checkout import ensure_checkout
```

and pass `middleware=[ensure_checkout]` to `define_deep_agent`.

**Checkpoint:**

> What's in /workspace/app? Show me the latest commit.

It should be **your fork**. In the trace, `ensure_checkout` runs before the
first model call, so the model never clones anything itself.

---

## Step 4: Give it a role (instructions)

```bash
cp add-ons/04-instructions/instructions.md my-agent/
```

**TODO:** three sections of `instructions.md`: *Verifying your change*,
*Rules*, and *Replying*. Each has questions to answer. Replace each
`<!-- TODO -->` comment with your answer. This file is the agent's system
prompt, and it's where its judgment comes from.

**Checkpoint:**

> Rename the "New game" button to "Restart". Don't open a pull request yet. Just make the change and tell me how you checked it.

A good result greps the whole repo and finds "New game" in **both**
`index.html` and `README.md`, checks the diff, and says how it verified. If it
only changed the button, tighten *Verifying your change*.

Then, in a **new thread**: `What does the button next to the Next preview say?`
It still says "New game". Each thread gets its own sandbox.

---

## Step 5: Connect it to GitHub (MCP connectors)

```bash
cp -R add-ons/05-tools/tools my-agent/
cat add-ons/05-tools/instructions.md.append >> my-agent/instructions.md
```

**TODO:** `tools/mcp.py`: list the GitHub tools Patch is allowed to use in
`include_tools`.

There's no wiring: MDA finds `tools/mcp.py` by name. The appended *Tools*
section tells Patch how to open a PR with those tools.

**Checkpoint:**

> What pull requests are open right now?

It reads your fork's name from the git remote and calls
`github__list_pull_requests`. The token comes from the `patch-github`
connection, which under `mda dev` reads `MDA_DEV_PATCH_GITHUB` from `.env`.

> The share button uses navigator.clipboard.writeText. Will that work for players on iPhone Safari?

This one uses `web__*` search, which LangSmith runs with no API key.

⚠️ **Right now Patch can open PRs with nobody approving them.** Don't ask it
to change anything until step 6.

---

## Step 6: Approve before it acts (human-in-the-loop)

Nothing to copy. This step is one argument in `agent.py`.

**TODO:** add `interrupt_on` to `define_deep_agent`, so the run pauses before
Patch **opens a pull request**. Allow only `approve` and `reject`, because
those are the only decisions Slack supports:

```python
interrupt_on={
    "<the tool name>": {"allowed_decisions": ["approve", "reject"]},
},
```

*Hint:* MCP tools are named `<server>__<tool>`. Which server, and which of the
tools you allowed in step 5?

**Checkpoint:**

> Add a key that toggles the ghost piece on and off. Use G. Then write a PR for it.

The run pauses with Approve / Reject. Reject it once and confirm no PR opens.
Then say `OK, go ahead` and approve. **You now have your first PR in your
fork.**

---

## Step 7: Teach it procedures (skills)

```bash
cp -R add-ons/07-skills/skills my-agent/skills
```

**TODO:** write `skills/add-a-feature/SKILL.md`, both its `description` and
its steps. `fix-a-bug` and `open-a-pull-request` are done for you. Read them
first.

At startup the agent sees only each skill's description, and it reads the full
file when a task matches. So the description decides *when* your skill is
used.

**Checkpoint:**

> Add WASD controls: A and D move left and right, S soft-drops, W rotates clockwise.

In the trace, it reads `/skills/add-a-feature/SKILL.md` early and follows your
steps. Did it update the controls in **both** `README.md` and `index.html`?

> I think hard drops give the wrong score. The README says 2 points per cell. Can you check and fix it?

It loads `fix-a-bug`, finds the code is already right, and stops without
inventing a fix.

---

## Step 8: Give it memory across conversations

```bash
cp add-ons/08-memory/memory.py my-agent/
cat add-ons/08-memory/instructions.md.append >> my-agent/instructions.md
```

There's no TODO here. Read the appended *Memory* section: it's the policy for
what goes in shared memory (`/memories/agent/`) and what goes in your private
memory (`/memories/user/`).

**Checkpoint:**

1. `From now on, open my PRs as drafts.` It saves this to
   `/memories/user/AGENTS.md`.
2. In a **new thread**: `Change the game title from TETRIS to BLOCKS.` The PR
   it proposes is a **draft**, which nobody asked for in this thread.

`mda dev` keeps memory on your laptop. Your deployed Patch starts with empty
memory.

---

## Step 9: Ship it to Slack

```bash
mkdir -p my-agent/channels
cp add-ons/09-slack/channels/slack.py my-agent/channels/
cat add-ons/09-slack/instructions.md.append >> my-agent/instructions.md
```

**TODO:** in `channels/slack.py`, give your bot a name everyone can tell apart
(`Patch-<your name>`) and a description.

Slack only works on a deployment, so now you deploy. From `my-agent/`:

```bash
uv run mda deploy
```

When the CLI prints a Slack authorization link, open it, pick the **webinar
workspace**, approve, and return to the terminal. Then store your GitHub token
in LangSmith and deploy again:

```bash
uv run mda connections create patch-github --secret-from-env MDA_DEV_PATCH_GITHUB
uv run mda deploy
```

Your bot DMs you in Slack.

**Checkpoint (in your DM with your bot):**

> On the pause screen, the title says "Paused". Make it "PAUSED".

You get **Approve / Reject buttons in Slack**. Approve, and it replies with the
PR link and attaches the diff. Then, in the same Slack thread:

> Also make the "Press P to resume" hint all caps.

The fix lands on the **same PR** as a second commit.

*Want the full demo moment?* Plant a bug in your fork (see
[Plant a bug](#plant-a-bug-optional)), screenshot it, and drop the screenshot
into the DM. Patch reads the image from `/workspace/attachments/`.

---

## Step 10: Run it on a schedule

```bash
cp -R add-ons/10-schedule/schedules my-agent/
```

**TODO:** make your own Slack channel (like `#patch-ada`), invite your bot to
it, and put the channel's ID in `schedules/pr_roundup.py`.

Schedules only run on a deployment, so `uv run mda deploy` again. Don't use
`--no-wait`, because that skips setting up the schedule.

**Checkpoint:** set `cron` to a few minutes ahead and redeploy. When it fires,
the roundup of your fork's open PRs appears in your channel. Set `cron` back
afterward.

---

## You're done when

- [ ] `grep -rn "TODO" my-agent --exclude-dir=.venv --exclude-dir=.mda` prints
      nothing
- [ ] Your Patch opened a PR in **your fork** from a Slack message, after you
      pressed **Approve** in Slack
- [ ] A follow-up in the same Slack thread added a commit to that PR
- [ ] Your PR roundup posted to your Slack channel on its own

---

## Plant a bug (optional)

From a clone of your fork:

```bash
sed -i '' 's/Press P to resume/Press Space to resume/' index.html tetris.js   # on Linux: sed -i
git commit -am "Update pause copy" && git push
```

Open `index.html` in a browser, start a game, press **P**, and screenshot the
overlay. Send it to your Patch with: *"The pause screen tells me to press Space
to resume, but Space doesn't unpause it."*

## Troubleshooting

| Symptom | Fix |
|---|---|
| `mda dev` fails building the sandbox | Read the `setup.sh` output in the terminal. Check that your LangSmith workspace has sandbox access |
| "Set PATCH_REPO in .env" | Add your fork, as `owner/name`, to `.env` |
| "Could not clone … into the sandbox" | Check `PATCH_REPO` is spelled right and your fork is public |
| No `github__*` tools in the trace | `include_tools` in `tools/mcp.py` still has `"TODO"` or misspelled names |
| GitHub 401/403/404 | Check the token covers your fork, with Contents + Pull requests read/write. Under `mda dev` it's `MDA_DEV_PATCH_GITHUB`; when deployed, recreate the connection |
| Run never pauses before the PR | The `interrupt_on` key must be the full `<server>__<tool>` name |
| `connections create` returns 403 | Your LangSmith role can't create connections. Use a workspace where you're an admin |
| Deployed run fails with `no agent connection is set for slug 'patch-github'` | Run `uv run mda connections create patch-github …` from `my-agent/`, then redeploy |
| Slack approval link says an admin must approve | Ask in the webinar Slack. The workspace admin approves the app |
| A new file seems ignored | Restart `mda dev`. New files are only picked up at startup |

## Clean up

When you're finished, delete the deployment. It asks you to confirm.

```bash
uv run mda delete
```

## Going further

- **Each person's own GitHub.** Switch the connection to
  `{"type": "user"}` with an OAuth connection. Each Slack user then connects
  their own GitHub account, and PRs open under their name. See
  [Connections](https://docs.langchain.com/langsmith/python/managed-deep-agents-connections).
- **Skip retyping files.** `push_files` makes the model write out every changed
  file in full. Write an authored tool that reads the files from the sandbox
  with `runtime.backend` instead. See
  [Tools](https://docs.langchain.com/langsmith/python/managed-deep-agents-tools).
- **Prove it keeps working.** Add a Harbor eval under `evals/tasks/`. See
  [Evals](https://docs.langchain.com/langsmith/python/managed-deep-agents-evals).
- **Call it from Claude Code.** See the
  [MCP endpoint](https://docs.langchain.com/langsmith/python/managed-deep-agents-mcp-endpoint).
