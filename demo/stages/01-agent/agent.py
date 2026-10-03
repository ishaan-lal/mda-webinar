"""Patch: fixes bugs and builds small features in a web game, then opens a PR.

The sandbox, Slack channel, memory, schedule, and MCP servers are declared by
where their files sit in the project. Only tools and middleware, which are
plain code, are imported here.
"""

from managed_deepagents import define_deep_agent

agent = define_deep_agent(
    name="patch",
    model="anthropic:claude-sonnet-5",
)
