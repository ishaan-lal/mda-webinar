"""MCP connectors: remote MCP servers whose tools the agent gets automatically.

Nothing here is imported in agent.py. MDA finds `mcp` in tools/mcp.py, builds
the MCP clients, and adds each server's tools as `<server>__<tool>`.
"""

from managed_deepagents import connections, define_mcp

mcp = define_mcp(
    servers={
        "github": {
            "transport": "http",
            "url": "https://api.githubcopilot.com/mcp/",
            "connection": connections.get("patch-github", {"type": "agent"}),
            "include_tools": [
                "create_branch",
                "push_files",
                "create_pull_request",
                "list_pull_requests",
            ],
        },
        "web": {
            "transport": "http",
            "url": "https://api.smith.langchain.com/v1/managed-tools/servers/parallel/mcp",
        },
    },
    throw_on_load_error=False,
)
