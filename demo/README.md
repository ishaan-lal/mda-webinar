# Demo: Building Patch

**Patch** is a [Managed Deep Agent](https://docs.langchain.com/langsmith/python/managed-deep-agents-overview)
that lives in Slack, fixes bugs in a small browser game, and opens pull requests
after a human approves them. In the webinar it's built live, one feature at a time.

[`patch/`](patch/) is the agent. It starts as a bare MDA project: just `agent.py`.
Each stage adds a file or two, applied with `stage.sh` from
[`../documentation/`](../documentation/).

## Setup

```bash
cd patch
uv sync
cp .env.example .env   # fill in LANGSMITH_API_KEY, LANGSMITH_WORKSPACE_ID,
                       # ANTHROPIC_API_KEY, MDA_DEV_PATCH_GITHUB
```

**Important**: MDA deployments are only available for paid LangSmith accounts. If you do not have a LangSmith Plus account, you can create a fully-provisioned temporary workspace by following the instructions [here](https://docs.google.com/document/d/1-NX0y7IA4tpVn8hf9fyhPbRQaSBPB03kkym3QRKRk8g/edit?usp=sharing). 


## Running it

Use two terminals:

```bash
# Terminal 1: documentation/
./stage.sh next     # apply the next stage and print the diff
./stage.sh status   # which stage patch/ is at
./stage.sh reset    # back to the bare agent

# Terminal 2: demo/patch/
uv run mda dev      # restart after each stage
```

## Stages

| # | Adds | Feature |
|---|---|---|
| 1 | `agent.py` | The agent definition, the only required file |
| 2 | `sandbox/`, `middleware/` | An isolated machine per thread, with the repo cloned in |
| 3 | `instructions.md` | Behavior, editable in Context Hub without a redeploy |
| 4 | `tools/mcp.py`, `skills/`, `interrupt_on` | GitHub tools, on-demand procedures, approval before a PR opens |
| 5 | `memory.py` | Shared and per-user memory across conversations |
| 6 | `channels/slack.py` | Slack, via `mda deploy` |
| 7 | `schedules/` | A weekday PR roundup posted to Slack |

For the full script (queries, talking points, and day-before setup), see
[`WALKTHROUGH.md`](../documentation/WALKTHROUGH.md).
