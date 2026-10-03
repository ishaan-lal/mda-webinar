# Managed Deep Agents Webinar

| Folder | What it is | Mirrors |
|---|---|---|
| [`demo/`](demo/) | **Patch**, an MDA that fixes bugs in a web game from Slack and opens PRs. It's built live in 10 stages: `stage.sh next` copies each pre-written feature into `patch/` and prints the diff. Comes with a presenter walkthrough with a query per stage | The Deep Agents webinar's journal-agent notebook |
| [`takehome/`](takehome/) | Students build **their own Patch** on their fork of `simple-game`, in the webinar Slack workspace. Same 10 steps as the demo: copy each `add-ons/` step into `my-agent/`, fill in its TODOs, and run a checkpoint. `solution/` has the finished agent, and `INSTRUCTORS.md` has the setup you need to do first | The Deep Agents 101 template notebook |

The Deep Agents materials were notebooks that built an agent cell by cell. An
MDA is a directory where each file's location turns a feature on, so both
halves build an agent **file by file**. Each step adds one file (or a line of
wiring), says what MDA does with it, and has one thing to try. The demo and the
take-home use the same pattern: a bare agent, plus pre-written pieces you copy
in.

## Why Patch for the demo

Patch builds on `mda-projects/bugfix-demo` and covers almost every feature
specific to MDA in a single story: *report a bug in Slack → the agent fixes it
in its own sandbox → you approve in Slack → a PR opens.*

| MDA feature | How Patch uses it |
|---|---|
| Instructions + Context Hub | Behavior only: verification, routing, reply style. Can be edited live without redeploying |
| Skills | `fix-a-bug`, `add-a-feature`, `open-a-pull-request`, written to work on any repo |
| Sandbox + `setup.sh` snapshot | Its own machine per thread, with git and Node baked in |
| Middleware + `runtime.backend` | Clones the repo into the thread's sandbox before the agent starts |
| MCP connectors + connections | GitHub's MCP server narrowed to 4 tools, with its token from a workspace connection. Plus managed web search with no key |
| Human-in-the-loop | Approve / Reject buttons in Slack before a PR opens |
| Memory (agent + user layers) | Shared repo notes. Per-person preferences ("open my PRs as drafts") |
| Slack channel + file exchange | Drop a bug screenshot in, get a `.patch` diff back |
| Schedules + `deliver_to` | Weekday open-PR roundup posted to a Slack channel |

The walkthrough ends with a "Why it's built this way" section. Its rule is that
the prompt holds judgment, and code and config hold plumbing and guarantees.
Compared with `bugfix-demo`, the repo URL and clone script moved out of the
prompt and into `config.py` and middleware. Repo safety now comes from the
token's scope rather than a prompt rule.

Slack Analyst covers sandbox, Slack, memory, and connectors too, but its demo
moments are charts and numbers. Patch's are actions: a PR you can click and a
button that gates it. It also shows human-in-the-loop, schedules, and
connections, which Slack Analyst doesn't.
