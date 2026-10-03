"""Make sure the repo is checked out before the agent starts working.

This is plumbing, not judgment, so it runs as code instead of being something
the model is asked to do. It runs before every turn but only clones once per
thread: each thread has its own sandbox, and a follow-up turn keeps the edits
from the turn before.
"""

from langchain.agents.middleware import before_agent
from managed_deepagents import ManagedDeepAgentRuntime

from config import CHECKOUT, REPO


@before_agent
async def ensure_checkout(state: object, runtime: ManagedDeepAgentRuntime) -> None:
    if runtime.backend is None:
        return None
    if not REPO:
        raise RuntimeError("Set PATCH_REPO in .env to your fork, like octocat/simple-game.")
    # A public repo needs no credentials to clone. For a private one, add a
    # sandbox proxy rule that injects the `patch-github` connection for github.com.
    result = await runtime.backend.aexecute(
        f"[ -d {CHECKOUT}/.git ] || "
        f"git clone --quiet --depth 1 https://github.com/{REPO}.git {CHECKOUT}"
    )
    if result.exit_code != 0:
        raise RuntimeError(f"Could not clone {REPO} into the sandbox: {result.output}")
    return None
