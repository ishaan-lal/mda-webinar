"""MCP connectors: remote MCP servers whose tools the agent gets automatically.

Nothing here is imported in agent.py. MDA finds `mcp` in tools/mcp.py, builds
the MCP clients, and adds each server's tools as `<server>__<tool>`.
"""

from managed_deepagents import connections, define_mcp

mcp = define_mcp(
    servers={
        # GitHub's hosted MCP server. The token isn't in this project: it's the
        # `patch-github` workspace connection, resolved at runtime ("agent" means
        # one credential for every caller). Under `mda dev` it reads
        # MDA_DEV_PATCH_GITHUB from .env instead.
        #
        # Scope the token to the one repo (your fork). The token, not the prompt, is what
        # keeps Patch from touching anything else.
        "github": {
            "transport": "http",
            "url": "https://api.githubcopilot.com/mcp/",
            "connection": connections.get("patch-github", {"type": "agent"}),
            # TODO(step 5): GitHub's server has ~46 tools. List ONLY the ones
            # Patch needs, by their raw MCP names. Patch has to be able to:
            #   - create a branch
            #   - push several changed files in one commit
            #   - open a pull request
            #   - list open pull requests (the schedule in step 10 uses this)
            # Tool names: https://github.com/github/github-mcp-server#tools
            "include_tools": ["TODO"],
        },
        # Web search that LangSmith runs for you. No API key, no connection.
        "web": {
            "transport": "http",
            "url": "https://api.smith.langchain.com/v1/managed-tools/servers/parallel/mcp",
        },
    },
    # If one server is down, start with the others instead of failing the run.
    throw_on_load_error=False,
)
