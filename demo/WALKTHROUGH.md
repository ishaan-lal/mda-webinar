# Managed Deep Agents Webinar: Building Patch, a bug-fixing agent in Slack

In this demo you build **Patch** live, one feature at a time. Patch lives in
Slack. You report a bug (or drop in a screenshot of one), and it works on the
game repo in its own sandbox, finds and fixes the cause, verifies the change,
asks a human to approve, and opens a pull request.

It starts as a bare agent: one file, two arguments. Each section adds one
feature by copying its files into the project. You show what changed, then run
a query that puts the new feature to work. Nothing is typed live.

The Deep Agents webinar built an agent cell by cell in a notebook. An MDA is a
**directory**, so here it's built file by file.

For topics not covered today, see the
[Managed Deep Agents docs](https://docs.langchain.com/langsmith/python/managed-deep-agents-overview).

---

## How the demo works

```text
demo/
  stage.sh      applies the next stage and prints what changed
  stages/       one folder per feature, already written
  patch/        the agent you're building (starts at stage 1)
```

Each section starts with one command:

```bash
./stage.sh next        # copies the stage's files into patch/ and prints a diff
```

The command prints every new file, a diff for every changed file (that's the
wiring, usually a line or two in `agent.py`), and any text appended to
`instructions.md`. Then restart `mda dev` and run the section's query.

| Command | Use |
|---|---|
| `./stage.sh next` | Apply the next stage (in order; it won't skip or repeat one) |
| `./stage.sh status` | Which stage `patch/` is at |
| `./stage.sh reset` | Back to the bare agent. Keeps `.env` and `.venv`, and wipes `.mda/` (local memory and threads) |
| `./stage.sh all` | The finished agent, for deploying |

**Two terminals:** one in `demo/` for `./stage.sh`, and one in `demo/patch/`
for `uv run mda dev`. Start `mda dev` normally the first time. After that,
restart it with `Ctrl+C` and then `uv run mda dev --no-browser`, and refresh
the Studio tab you already have open.

### Studio first, Slack once

**Deploy the finished agent the day before. Build stages 1–8 in local Studio
(`mda dev`), then switch once to Slack (the deployment) for stages 9–10.**

- **Studio shows the internals.** Stages 1–8 are about how each piece works:
  the middleware step before the model, the skill file it reads, the arguments
  on the approval card. Studio's trace shows all of that. Slack shows only the
  final reply.
- **Slack is the finale.** By stage 9, your local `patch/` has caught up to
  what's deployed, and "here it is in Slack" lands as the payoff.
- **Don't run `mda deploy` live.** A build plus a sandbox bake takes minutes,
  and Slack setup needs a browser approval. Show the command and yesterday's
  output instead.

> **Fallback:** if `mda dev` misbehaves in rehearsal, you can skip the live
> build. Show each stage's diff with `./stage.sh next`, and run the queries in
> the *deployed* agent's Studio, which already has every feature.

Say these out loud at the switch. **Memory:** `mda dev` keeps memory on your
laptop, so the "drafts" preference from stage 8 doesn't follow you into Slack.
**GitHub token:** under `mda dev`, the `patch-github` connection reads
`MDA_DEV_PATCH_GITHUB` from `.env`. Deployed, it reads the workspace
connection. The code is identical.

### Run of show

| Stage | Adds | Where | Query (short) | Opens a PR? | ~min |
|---|---|---|---|---|---|
| 1 | `agent.py` | Studio | What's in your workspace? Git/Node versions? | | 3 |
| 2 | `sandbox/` | Studio | *Same query*, now with a real machine | | 3 |
| 3 | `middleware/` | Studio | What's in /workspace/app? Latest commit? | | 3 |
| 4 | `instructions.md` | Studio | Rename "New game" → "Restart", then a new thread | | 5 |
| 5 | `tools/mcp.py` | Studio | Open PRs? / Safari clipboard? | | 5 |
| 6 | `interrupt_on` | Studio | Ghost toggle on G: reject, then approve | ✅ #1 | 6 |
| 7 | `skills/` | Studio | "Hard drop score is wrong" | | 4 |
| 8 | `memory.py` | Studio | Drafts, then TETRIS → BLOCKS | ✅ #2 (draft) | 5 |
| 9 | `channels/` + deploy | **Slack** | Context Hub edit, screenshot bug, follow-up | ✅ #3 | 10 |
| 10 | `schedules/` | Slack | The roundup lists #1–#3 | | 3 |

---

## Setup: the day before

1. **Fill in `.env`.**
   ```bash
   cd demo/patch
   uv sync
   cp .env.example .env
   ```
   Fill in `LANGSMITH_API_KEY`, `LANGSMITH_WORKSPACE_ID`, `ANTHROPIC_API_KEY`,
   and `MDA_DEV_PATCH_GITHUB`, a fine-grained PAT scoped to the repo with
   Contents + Pull requests read/write. `PATCH_REPO` defaults to
   `ishaan-lal/simple-game`.
2. **Set the schedule's Slack channel** in
   `stages/10-schedule/schedules/pr_roundup.py`.
3. **Build the finished agent and deploy it.** Approve the Slack authorization
   link when the CLI prints it. The bot then DMs you.
   ```bash
   cd demo
   ./stage.sh all
   cd patch
   uv run mda deploy
   uv run mda connections create patch-github --secret-from-env MDA_DEV_PATCH_GITHUB
   uv run mda deploy
   ```
   If `connections create` returns 403, your workspace role can't create
   connections. Use a workspace where it can. As a stopgap, in
   `stages/05-tools/tools/mcp.py`, replace the `connection` line with
   `"headers": {"Authorization": f"Bearer {os.environ.get('GITHUB_TOKEN', '')}"}`
   (and `import os`), then put `GITHUB_TOKEN` in `.env`. That's how bugfix-demo
   ran.
4. **Invite the Patch bot** to the schedule's channel.
5. **Rehearse the whole thing from `./stage.sh reset`.** This also warms the
   sandbox snapshot. The first `mda dev` after stage 2 builds it, which can
   take a few minutes, and later runs reuse it. If the `mda dev` banner says
   it's using a local temporary folder instead of a sandbox, fix sandbox
   access before the webinar.
6. **Reset everything:** close the rehearsal PRs and delete their branches,
   then run `./stage.sh reset`.
7. **Don't edit `stages/` after the deploy,** so local and deployed match.
8. **Plant the demo bug and take the screenshot.** See
   [Plant the demo bug](#appendix-plant-the-demo-bug).
9. **On the morning of,** confirm the 9:03am PT roundup posted to the channel.
   If the webinar is before then or on a weekend, see stage 10.

---

## 1: An agent is a directory

`patch/` starts with nothing but the definition. There's no command to run
here: `./stage.sh reset` already put stage 1 in place.

**Show:** `patch/agent.py`

```python
from managed_deepagents import define_deep_agent

agent = define_deep_agent(
    name="patch",
    model="anthropic:claude-sonnet-5",
)
```

**Point out:**

- This is the only required file. `define_deep_agent` takes the same arguments
  as `create_deep_agent`, minus the ones MDA owns: `backend`, `store`,
  `checkpointer`, `memory`, `skills`, and `system_prompt`.
- It returns a *definition*, and MDA compiles and hosts it. You still get the
  whole Deep Agents harness, including planning, file tools, and subagents.

**Run it:** `uv run mda dev`, then in Studio:

> What's in your workspace? And what versions of git and Node can you run?

**Look for:** an empty workspace, and no way to run commands. The harness gives
it file tools that work on files in the agent's state (like `journal.md` in the
Deep Agents webinar), but there's no machine underneath. Remember this answer.

---

## 2: Give it a computer

```bash
./stage.sh next
```

**Adds:** `sandbox/__init__.py`, `sandbox/setup.sh`. No wiring, so `agent.py`
is unchanged.

```python
sandbox = define_sandbox(idle_ttl_seconds=1800, default_timeout=300)
```

**Point out:**

- **The folder's presence is the switch.** MDA sees `sandbox/` and gives every
  conversation (thread) its own isolated machine.
- `setup.sh` runs **once**, when the snapshot is built, not per conversation.
  It installs **tooling only** (git and Node). Each new thread starts from that
  snapshot.

**Run it:** restart `mda dev`. In a **new thread**, send the **same query**:

> What's in your workspace? And what versions of git and Node can you run?

**Look for:** `execute` calls running real commands, with git and Node versions
from the snapshot. Same question, different agent.

---

## 3: Get the repo into the sandbox, with middleware

```bash
./stage.sh next
```

**Adds:** `config.py`, `middleware/checkout.py`. **Wiring:** two lines in
`agent.py` (the diff shows them).

```python
@before_agent
async def ensure_checkout(state, runtime: ManagedDeepAgentRuntime) -> None:
    await runtime.backend.aexecute(
        f"[ -d {CHECKOUT}/.git ] || git clone --depth 1 https://github.com/{REPO}.git {CHECKOUT}"
    )
```

**Point out:**

- `config.py` is the **only** place the repo is named. It comes from
  `PATCH_REPO`, so the demo can run on a fork without code changes.
- This is plain LangChain middleware. MDA adds `runtime.backend`, the current
  thread's sandbox.
- Why not just tell the model "first, clone the repo"? Cloning is **plumbing,
  not judgment**. A prompt costs a tool call, can be skipped, and puts a URL in
  the prompt. A `before_agent` hook runs every time, before the model sees
  anything.
- Why not bake the repo into the snapshot? The repo changes with every merged
  PR, so a baked copy would be stale.

**Run it:** restart `mda dev`. In a **new thread**:

> What's in /workspace/app? Show me the latest commit.

**Look for:** in the trace, the `ensure_checkout` step runs *before* the first
model call. The model's first tool call reads a repo that's already there, and
it never clones anything itself.

---

## 4: Give it a role, with instructions

```bash
./stage.sh next
```

**Adds:** `instructions.md`. No wiring: like `sandbox/`, MDA finds it by name.

**Point out:**

- This replaces `system_prompt=`. It's plain Markdown, inserted into every run.
- It holds **behavior only**: how to verify a change, when to stop, how to
  reply. It doesn't name the repo or describe its layout. The agent reads the
  repo's own README for that.
- On deploy it syncs to **Context Hub**, where you can edit it without
  redeploying. You'll do that in stage 9.
- Later stages append their own sections to this file. Watch for them in the
  diffs.

**Run it:** restart `mda dev`. In a **new thread**:

> Rename the "New game" button to "Restart". Don't open a pull request yet. Just make the change and tell me how you checked it.

**Look for:** each step comes from a section of the instructions.

1. **Reads `README.md` first** (*Your workspace*).
2. **Greps the whole repo** for "New game" (*Completeness*). It finds the
   button in `index.html` **and** the controls table in `README.md`, so a
   change to the button alone would be incomplete.
3. **Reads the diff back** (*Read it back*). It skips `node --check`, because
   no JavaScript changed.
4. **Replies in a few lines** with what changed and how it checked
   (*Replying*). It can't open a PR anyway, since it has no GitHub tools yet.

**Then the isolation beat.** In **another new thread**:

> What does the button next to the Next preview say?

It says "New game". The rename lives only in the first thread's machine. Each
thread gets its own sandbox, so two people in Slack never see each other's
half-finished edits.

---

## 5: Let it reach the outside world, with tools

```bash
./stage.sh next
```

**Adds:** `tools/mcp.py`. **No wiring:** like `sandbox/`, MDA finds it by
name, so `agent.py` doesn't change. **Appends:** a *Tools* section to
`instructions.md`, covering how to open a PR with these tools.

```python
mcp = define_mcp(
    servers={
        "github": {
            "transport": "http",
            "url": "https://api.githubcopilot.com/mcp/",
            "connection": connections.get("patch-github", {"type": "agent"}),
            "include_tools": ["create_branch", "push_files", "create_pull_request", "list_pull_requests"],
        },
        "web": {
            "transport": "http",
            "url": "https://api.smith.langchain.com/v1/managed-tools/servers/parallel/mcp",
        },
    },
)
```

**Point out:**

- **Two servers, declared, not coded.** No MCP client, no tool-loading code.
  The tools show up as `github__push_files`, `web__...`, and so on.
- **`include_tools`** narrows GitHub's ~46 tools to the four Patch needs. Less
  for the model to choose from, and less it could do wrong.
- **Connections keep the credential out of the project.** The GitHub token
  isn't in the code or in a deployment secret. It lives in the LangSmith
  workspace under `patch-github`, and `connections.get(...)` resolves it at
  runtime. Rotating it needs no redeploy. Under `mda dev`, the same line reads
  `MDA_DEV_PATCH_GITHUB` from `.env`.
- **`{"type": "agent"}` vs `{"type": "user"}`.** Patch uses one token for
  everyone. Switch to `"user"` with an OAuth connection, and each Slack user
  connects their own GitHub, so PRs open under their name. MDA runs the OAuth
  round-trip for you.
- **The token is the guardrail.** It's a fine-grained token scoped to this one
  repo, so Patch *can't* touch anything else, whatever a message says. And the
  sandbox has no credentials at all: it can edit files, but only these four
  tools reach GitHub.
- **`web`** is a managed tool: web search that LangSmith runs, with no API key.

**Run it:** restart `mda dev`. In a **new thread**:

> What pull requests are open right now?

**Look for:** the agent reads `owner/repo` from the checkout's git remote, then
calls `github__list_pull_requests`, with no token in sight.

> The share button uses navigator.clipboard.writeText. Will that work for players on iPhone Safari?

**Look for:** `web__*` calls with a cited source, plus a check of `tetris.js`
to see how the button actually calls the API.

**Say it:** *Right now this agent can open PRs with nobody approving them.*
That's the next stage, so don't ask it to change anything yet.

---

## 6: Approve before it acts

```bash
./stage.sh next
```

**Wiring:** `interrupt_on` in `agent.py`. That's the whole stage.

```python
interrupt_on={
    "github__create_pull_request": {"allowed_decisions": ["approve", "reject"]},
},
```

**Point out:**

- This is the same `interrupt_on` as the Deep Agents webinar, now applied to
  an **MCP** tool (server name + `__` + tool name). Last time, resuming meant
  `Command(resume=...)` in a notebook cell. Here the checkpointer is managed,
  Studio shows Approve / Reject, and in Slack, MDA renders the buttons.
- The gate is on **opening the PR**, the step a reviewer cares about. Its card
  shows the title and body, which is readable in Slack. Branch and commit
  happen first, so a rejection leaves a branch behind.
- Slack supports `approve` and `reject` only, so that's all this agent allows.

**Run it:** restart `mda dev`. In a **new thread**:

> Add a key that toggles the ghost piece on and off. Use G.

**Look for:** it reads the README, edits `tetris.js`, runs `node --check`,
creates a branch, pushes the files, and then the run **pauses** on
`github__create_pull_request`. The card shows the title, body, and branch.

1. **Reject** it. Patch says so in one line. No PR is opened, but its branch
   is on GitHub.
2. Say `OK, go ahead and open it.` **Approve** the new card.
3. Open the PR in GitHub. *(PR #1)*

---

## 7: Teach it procedures, with skills

```bash
./stage.sh next
```

**Adds:** `skills/fix-a-bug/`, `skills/add-a-feature/`,
`skills/open-a-pull-request/`. No wiring.

**Point out:**

- At startup the agent sees only each skill's `name` and `description`. It
  reads the full `SKILL.md` when a task matches, so a detailed procedure costs
  no context until it's needed.
- **Use** instructions for always-on behavior, skills for procedures loaded
  when needed, and memory (next stage) for things it learns.
- The skills are **repo-agnostic**. "In a web app, user-visible text is often
  written twice" holds for any repo.
- Show `fix-a-bug` step 3: *if the code already behaves correctly, stop.*

**Run it:** restart `mda dev`. In a **new thread**:

> I think hard drops give the wrong score. The README says 2 points per cell. Can you check and fix it?

**Look for:** a `read_file` of `/skills/fix-a-bug/SKILL.md` early in the trace.
Then it greps the README and `tetris.js` (`score += cells * 2`), concludes the
code is already right, and **stops without proposing a PR**. That's step 3:
don't invent a fix.

---

## 8: Give it memory across conversations

```bash
./stage.sh next
```

**Adds:** `memory.py`. **Appends:** a *Memory* section to `instructions.md`,
which is the policy for what goes where.

```python
memory = define_memory(agent=MemoryLayer(), user=MemoryLayer())
```

**Point out:**

- The checkpointer gives memory **within** a conversation, and MDA manages
  that. `memory.py` adds memory **across** conversations.
- **Two layers**, each a folder the agent reads and writes with its normal file
  tools:
  - `/memories/agent/` is shared by everyone: repo facts and gotchas.
  - `/memories/user/` is private to each person: their preferences.
- `AGENTS.md` in each layer is loaded into every run.
- **Privacy defaults:** user memory mounts in Slack DMs and for Studio users,
  and is **off in shared Slack channels**.

**Run it:** restart `mda dev`. In a **new thread**:

1. > From now on, open my PRs as drafts.

   **Look for:** a write to `/memories/user/AGENTS.md`, and a one-line
   confirmation.
2. In **another new thread**:
   > Change the game title from TETRIS to BLOCKS.

   **Look for:** it finds the title in more than one place (`<title>`, `<h1>`,
   README), and the approval card has `draft: true`, which nobody asked for in
   this thread. Approve it. *(PR #2, a draft)*

---

## 9: Ship it, and put it in Slack

```bash
./stage.sh next
```

**Adds:** `channels/slack.py`. **Appends:** a *Slack* section to
`instructions.md`, covering attachments in and diffs out.

```python
channel = channels.slack(
    name="Patch",
    description="Fixes bugs and builds small features in the Tetris game, then opens a PR.",
    background_color="#1C3C3C",
)
```

**Point out:**

- **That's the whole Slack integration.** No Slack app to create, no bot token
  or signing secret in `.env`.
- Each Slack thread maps to its own agent thread (and sandbox). DMs and
  @mentions start runs, and replies in the thread continue them.
- **Files go both ways:** uploads land in `/workspace/attachments/`, and
  `attach_file` sends files back.
- Slack needs a deployment. Show the command, and the output from yesterday's
  deploy of this exact project:
  ```bash
  uv run mda deploy
  ```
  That one command synced `instructions.md` and `skills/` to Context Hub, built
  the sandbox snapshot, deployed everything on LangSmith Agent Server, set up
  the Slack app, and created the cron schedule (stage 10).

**Switch to Slack now.** Say the two notes from
[Studio first, Slack once](#studio-first-slack-once): memory and the token.

**Run it (Slack DM with Patch):**

1. **Context Hub, live.** Ask:
   > Hi! What can you do?

   Then, in the deployment's **Context Hub**, change the first line of
   *Replying* in `instructions.md` to `Reply in one sentence.` and save. Ask
   again:
   > What can you do?

   **Look for:** a one-sentence reply. Behavior changed with **no redeploy**.
   Change the line back afterward. Otherwise the next `mda deploy` asks
   whether to overwrite the Hub-edited file.
2. **The bug report.** Upload the screenshot of the planted bug, with:
   > The pause screen tells me to press Space to resume, but Space doesn't unpause it.

   **Look for:**
   - It reads the screenshot from `/workspace/attachments/`.
   - The `fix-a-bug` skill finds the text in **both** `index.html` and
     `tetris.js`, fixes both, and re-greps to prove nothing is left.
   - **Approve / Reject** buttons appear in the thread. Approve.
   - It replies with the PR link and attaches `change.patch`. *(PR #3)*
3. **Follow-up, same thread:**
   > Also make the pause title all caps.

   **Look for:** a `github__push_files` to the **same branch**, and a reply
   with the same PR link, which now has two commits. The thread kept its
   sandbox, so the first fix was still there. There's no second approval,
   because the gate is on opening a PR, and this adds to one that's already
   under review.

---

## 10: Run it on a schedule

```bash
./stage.sh next
```

**Adds:** `schedules/pr_roundup.py`. No wiring. This brings `patch/` level
with the deployment.

```python
schedule = define_schedule(
    cron="3 9 * * 1-5",
    timezone="America/Los_Angeles",
    prompt="List this repository's open pull requests with github__list_pull_requests. ...",
    deliver_to={"channel": "slack", "to": {"type": "provider_conversation", "conversation_id": "C..."}},
)
```

**Point out:**

- One file per schedule, and the file name is the schedule name. The agent
  runs **without anyone messaging it**, and `deliver_to` posts the result to a
  Slack channel.
- Declarations are read at compile time **without running the file**, so every
  value must be a literal, with no env vars or function calls.
- Schedules never fire under `mda dev`. They only run on a deployment.

**Show it:** this morning's roundup in the Slack channel. Then DM Patch the
schedule's own prompt, to preview tomorrow's:

> List this repository's open pull requests with github__list_pull_requests. Reply with one line per PR: title, link, and days open. Flag any open more than 3 days.

**Look for:** PRs #1–#3 from this webinar, with #2 marked as a draft.

The schedule's prompt doesn't name the repo either. The scheduled run gets a
sandbox and a checkout like any other run, so the agent reads the repo from the
git remote.

> No roundup yet today (before 9:03am PT, or a weekend)? During rehearsal, set
> `cron` to a few minutes ahead in `stages/10-schedule/`, redeploy, capture the
> post, then set it back and redeploy.

---

## Why it's built this way

The rule Patch follows: **the prompt holds judgment, and code holds plumbing
and guarantees.**

| Concern | Where it lives | Why not in the prompt |
|---|---|---|
| Which repo | `config.py` (from `PATCH_REPO`) | One place to change. The agent reads it back from the git remote |
| Getting the repo into the sandbox | `middleware/checkout.py` | Runs every time, costs no tool call, can't be skipped |
| Tooling (git, Node) | `sandbox/setup.sh` | Baked once into the snapshot instead of installed per thread |
| Talking to GitHub | `tools/mcp.py`, narrowed with `include_tools` | Declared, not coded. Four tools instead of ~46 |
| Only this repo, ever | The token's scope | A credential limit holds no matter what a message says |
| The GitHub credential | `patch-github` connection | Not in code or a deployment secret, and rotates without a redeploy |
| Approval before a PR opens | `interrupt_on` on `github__create_pull_request` | The pause is enforced by the runtime, not requested in a prompt |
| How to fix a bug, what a PR says | `skills/` | This *is* judgment, so it belongs in prose |
| What it learned about this repo | `/memories/agent/` | Discovered at runtime, not hand-written |

**A trade-off to mention if asked:** `push_files` takes each file's full
contents, so the model writes out every changed file in its tool call. That's
fine for a small repo like this one. For large files, an authored tool that
reads the files straight from the sandbox through `runtime.backend` avoids it,
at the cost of writing that tool.

---

## Wrap-up

Ten stages, each a file or two:

| Stage | You added | MDA ran |
|---|---|---|
| 1 | `agent.py` | The Deep Agents harness, durable threads, Agent Server hosting |
| 2 | `sandbox/` | One isolated machine per thread, a snapshot baked from `setup.sh` |
| 3 | `middleware/` | `runtime.backend` into the thread's sandbox |
| 4 | `instructions.md` | Context Hub sync, editable without a redeploy |
| 5 | `tools/mcp.py` | MCP clients and tool loading, credentials from a connection, a managed search tool |
| 6 | `interrupt_on` | The pause, the checkpoint, and Approve / Reject buttons in Slack |
| 7 | `skills/` | Skills loaded on demand, synced to Context Hub |
| 8 | `memory.py` | Shared and per-user memory, with privacy defaults |
| 9 | `channels/slack.py` | A Slack app, event handling, thread mapping, file transfer |
| 10 | `schedules/` | Cron jobs, with results posted to Slack |

**Also in MDA, not shown today:**

- **Identity** (`identity.py`): Supabase or your own backend, for private
  per-user threads in your own app.
- **User-owned connections**: each person authorizes their own GitHub, Notion,
  or Linear account.
- **Agent-owned interrupts**: post your own Block Kit form in Slack and resume
  the run when it's submitted.
- **Sandbox proxy**: inject a connection into the sandbox's outbound requests,
  for example to clone a private repo, without the sandbox seeing the token.
- **MCP endpoint**: call a deployed agent as a tool from Claude Code or any MCP
  client.
- **Subagents** and **Harbor evals** (`evals/tasks/`).

The take-home works the same way, with a bare agent and add-ons you copy in:
[`../takehome/`](../takehome/README.md).

**After the webinar:** close PRs #1–#3 (or merge them), delete their branches,
revert the planted bug if PR #3 isn't merged, and run `./stage.sh reset`.

---

## Appendix: plant the demo bug

The demo bug is wrong text on the pause screen. It lives in two files, which is
what the `fix-a-bug` skill's "find every occurrence" step is for.

From your own checkout of the repo:

```bash
git checkout main && git pull
sed -i '' 's/Press P to resume/Press Space to resume/' index.html tetris.js
git diff                          # two lines: index.html:31 and tetris.js:389
git commit -am "Update pause copy"
git push
```

Open `index.html`, start a game, press **P**, and screenshot the overlay.

## Appendix: backup queries

| Stage | Backup query |
|---|---|
| 4 | `Rename the "Hold" panel heading to "Saved". Don't open a pull request; tell me how you checked it.` |
| 5 | `What does the Vibration API do on Android vs iOS? Would it work for a line-clear buzz?` |
| 6 | `Add WASD controls: A and D move, S soft-drops, W rotates clockwise.` |
| 7 | `The Z key rotates the wrong way. It should be counter-clockwise.` (It already is, so Patch should say no change is needed.) |
| 8 | `Remember for everyone: user-visible text lives in both index.html and tetris.js.` Then show `/memories/agent/AGENTS.md`. |
| 9 | Without a screenshot: `On the pause screen, the hint says to press Space to resume, but only P works.` |
