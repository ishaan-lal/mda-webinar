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

For anything not covered here, see the
[Managed Deep Agents docs](https://docs.langchain.com/langsmith/python/managed-deep-agents-overview).

---

## What you need

- A **LangSmith API key**.
- An **Anthropic API key**
- [**uv**](https://docs.astral.sh/uv/getting-started/installation/)
- A **GitHub** account

**Important**: MDA deployments are only available for paid LangSmith accounts. If you do not have a LangSmith Plus account, you can create a fully-provisioned temporary workspace by following the instructions [here](https://docs.google.com/document/d/1-NX0y7IA4tpVn8hf9fyhPbRQaSBPB03kkym3QRKRk8g/edit?usp=sharing). 

---

## Setup

1. **Fork the game.** Fork
   [`ishaan-lal/simple-game`](https://github.com/ishaan-lal/simple-game) to
   your GitHub account. Patch only ever works on your fork.
    **IMPORTANT: Fork the game repo. This is different from the current (take-home exercise) repo**.
2. **Make a GitHub token for your fork only.** In GitHub, go to *Settings →
   Developer settings → Fine-grained tokens → Generate new token*:
   - *Repository access:* **Only select repositories** → your fork
   - *Permissions:* **Contents** read and write, and **Pull requests** read and
     write

3. **Fill in `.env`.**
   ```bash
   cd my-agent
   uv sync
   cp .env.example .env
   nano .env
   ```
   You can also edit `.env` by opening the code in an IDE. 


    Fill in `LANGSMITH_API_KEY`, `ANTHROPIC_API_KEY`,
   `PATCH_REPO` (your fork, like `ishaan-lal/simple-game`), and
   `MDA_DEV_PATCH_GITHUB` (the token).

---

## How each step works

Keep two terminals open: one in `takehome/` for copying (known henceforth as **Terminal One**), and one in
`takehome/my-agent/` for `uv run mda dev` (**Terminal Two**).

1. **Copy** the step's add-on files into `my-agent/` (each step gives the copy
   commands).
2. **Fill in the `TODO`s.** Every one is marked `TODO(step N)` and explains
   what to write. 
3. **Restart `mda dev`** (`Ctrl+C`, then `uv run mda dev`). New files are only
   picked up when it starts.
4. **Run the checkpoint** query in Studio and check the trace. Start a **new
   thread** for each step, so earlier conversations don't get in the way.

Stuck? The finished file for every step is in `solution/`.

---

## Step 1: Run the bare agent

As it is currently set up, the agent is completely bare. `my-agent/agent.py` defines the agent as:
```python
agent = define_deep_agent(
    name="TODO",
    model="anthropic:claude-sonnet-5",
)
```

As it's defined, the agent is just a deep agent with a model and a harness. It has no customization yet. We'll build up the MDA as we go.

**TODO:** in `my-agent/agent.py`, give your agent a `name`.

```bash
uv run mda dev
```

**Checkpoint:**

In LangSmith Studio, go to the chat tab, and ask the following question:

> What's in your workspace? And what versions of git and Node can you run?

The agent should indicate that it has tools, but it should not be able to name the versions of git and Node, because a sandbox has not yet configured. Let's add one.

---

## Step 2: Give the agent a sandbox

In **Terminal 1**, run:
```bash
cp -R add-ons/02-sandbox/sandbox my-agent/sandbox
```

Review the two files that were copied over:

- `sandbox/__init__.py` declares the sandbox. The folder's presence is what
  turns it on: every conversation (thread) now gets its own isolated machine.
- `sandbox/setup.sh` runs **once**, when the sandbox snapshot is built, not on
  every conversation. It installs only tooling (git and Node), and every new
  thread starts from that snapshot.

**Checkpoint:** In **Terminal Two** re-run `uv run mda dev`, then send the **same** query as step 1: 

> What's in your workspace? And what versions of git and Node can you run?

This time, the agent should return versions of git and Node that have been configured in its sandbox.

---

## Step 3: Get your fork into the sandbox (middleware)

The agent will use the sandbox to write code and test it out. For this, the agent needs access to the codebase. We'll set that up by configuring middleware.

In **Terminal One**, run the following commands:

```bash
cp add-ons/03-checkout/config.py my-agent/
cp -R add-ons/03-checkout/middleware my-agent/
```

Skim the two files:

- `config.py` is the only place in the project that names the repo. It reads
  `PATCH_REPO` from `.env`.
- `middleware/checkout.py` defines a deterministic routine that clones your fork into the sandbox before the model runs, once per thread. 

**TODO (wiring):** unlike a sandbox, middleware is code, so `agent.py` has to
import it. In `agent.py`, add:

```python
from middleware.checkout import ensure_checkout
```

and pass `middleware=[ensure_checkout]` to `define_deep_agent`.

**Checkpoint:**

In **Terminal Two**, restart `uv run mda dev`, and in the chat, as the agent: 

> What's in /workspace/app? Show me the latest commit.

It should be **your fork**. In the trace, `ensure_checkout` runs before the
first model call, so the model never clones anything itself.

---

## Step 4: Give it a role (instructions)

The agent could benefit from having configured behavior and instructions. We will set that up now.

In **Terminal One**, run:

```bash
cp add-ons/04-instructions/instructions.md my-agent/
```

**TODO:** three sections of `instructions.md`: *Verifying your change*,
*Rules*, and *Replying*. Each has questions to answer. Replace each
`<!-- TODO -->` comment with your answer. This file is the agent's system
prompt, and it's where its judgment comes from.

**Checkpoint:**

In **Terminal Two**, re-run `uv run mda dev`, and chat with the agent:

> Rename the "New game" button to "Restart". Don't open a pull request yet. Just make the change and tell me how you checked it.

A good result greps the whole repo and finds "New game" in **both**
`index.html` and `README.md`, checks the diff, and says how it verified. If it
only changed the button, tighten *Verifying your change*.

Then, in a **new thread**: `What does the button next to the Next preview say?`
It still says "New game". Each thread gets its own sandbox.

---

## Step 5: Connect it to GitHub (MCP connectors)

At this point, our agent can write code, test it out in the sandbox, and follow the instructions we have specified for it. Now, we want the agent to connect to GitHub so as to draft PRs. The agent will connect to GitHub via MCP.


In **Terminal One**, run:
```bash
cp -R add-ons/05-tools/tools my-agent/
cat add-ons/05-tools/instructions.md.append >> my-agent/instructions.md
```

**TODO:** `tools/mcp.py`: list the GitHub tools Patch is allowed to use in
`include_tools`.

At minimum, be sure to include the following: `create_branch`, `push_files`, `create_pull_request`, `list_pull_requests`.

There's no wiring: MDA finds `tools/mcp.py` by name. The appended *Tools*
section tells Patch how to open a PR with those tools.

**IMPORTANT**: The MCP uses a connection:
```
"connection": connections.get("patch-github", {"type": "user"})
```

We must define a connection so the agent can obtain a value. To do so, we will set up a user-scoped connection via OAuth.

First, register a GitHub OAuth app [here](https://github.com/settings/developers), making sure to utilize the forked repository, and obtain the `CLIENT ID`. 

Now, in **Terminal One**, run the following to create the connection:
```bash
uv run mda connections create patch-github --oauth github --client-id 
```

**Checkpoint:**

In **Terminal Two**, re-run `uv run mda dev`

> What pull requests are open right now?

It reads your fork's name from the git remote and calls
`github__list_pull_requests`. The token comes from the `patch-github`
connection, which under `mda dev` reads `MDA_DEV_PATCH_GITHUB` from `.env`.

> The share button uses navigator.clipboard.writeText. Will that work for players on iPhone Safari?

This one uses `web__*` search, which LangSmith runs with no API key.


---

## Step 6: Approve before it acts (human-in-the-loop)

At this point, the agent has a lot of power. We'll now aim to gate some of its capabilities, particularly its ability to create PRs, by configuring Human-in-the-loop.

**TODO:** In `agent.py` add `interrupt_on` to `define_deep_agent`, so the run pauses before Patch **opens a pull request**. Allow only `approve` and `reject`, because
those are the only decisions Slack supports:

```python
interrupt_on={
    "<the tool name>": {"allowed_decisions": ["approve", "reject"]},
},
```

*Hint:* MCP tools are named `<server>__<tool>`. Which server, and which of the
tools you allowed in step 5?

**Checkpoint:**

In **Terminal Two**, re-run `uv run mda dev`, and chat:

> Add a key that toggles the ghost piece on and off. Use G. Then write a PR for it.

The run pauses with Approve / Reject. Reject it once and confirm no PR opens.
Then say `OK, go ahead` and approve. **You now have your first PR in your
fork.**

---

## Step 7: Teach it procedures (skills)

Let's now set up some skills for the agent.

In **Terminal One**, run

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

We'll now configure memory so that the agent can remember critical information at both a user-scope and an agent-scope.

In **Terminal One**, run:

```bash
cp add-ons/08-memory/memory.py my-agent/
cat add-ons/08-memory/instructions.md.append >> my-agent/instructions.md
```

There's no TODO here. Read the appended *Memory* section: it's the policy for
what goes in shared memory (`/memories/agent/`) and what goes in your private
memory (`/memories/user/`).

**Checkpoint:**

Re-run `uv run mda dev` in **Terminal Two**, and send the agent the following:

1. `From now on, open my PRs as drafts.` It saves this to
   `/memories/user/AGENTS.md`.
2. In a **new thread**: `Change the game title from TETRIS to BLOCKS.` The PR
   it proposes is a **draft**, which nobody asked for in this thread.

`mda dev` keeps memory on your laptop. Your deployed Patch starts with empty
memory.

---

## Step 9: Ship it to Slack

It's time to get the agent into Slack! 

In **Terminal One**, run the following:

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

You can choose to utilize your own personal Slack workspace, or join the MDA [webinar slack workspace](https://join.slack.com/t/langchain-pmw7732/shared_invite/zt-4by2uw10m-MVupHxkp6osIwOxqT8~mqw). This is where you can deploy your agent and interact with it. 

When the CLI prints a Slack authorization link, open it, pick the desired workspace, approve, and return to the terminal. Then, in **Terminal Two** store your GitHub token
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

---

## Step 10: Run it on a schedule

Configure a schedule with your agent!

In **Terminal One**, run:

```bash
cp -R add-ons/10-schedule/schedules my-agent/
```

`pr_roundup.py` defines a schedule for the agent -- it will list the repository's open pull requests at the cadence specified by the cron expression. Configure the `cron` expression to your preference, and rewrite the `prompt` if you wish. 

If you are using the MDA webinar Slack workspace, you may set `conversation_id` to the value of `C0C6CAMRA9H`. When your agent runs at the scheduled time, it will post its response in the `#bot-party` channel.

Schedules only run on a deployment, so `uv run mda deploy` again.

**Checkpoint:** set `cron` to a few minutes ahead and redeploy. When it fires,
the roundup of your fork's open PRs appears in your channel. Set `cron` back
afterward.

---


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
