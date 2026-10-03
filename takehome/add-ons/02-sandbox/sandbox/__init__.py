"""The agent's own computer: an isolated filesystem and shell, one per conversation.

The directory's presence turns the sandbox on. setup.sh, if present, runs once
at deploy (or `mda dev`) time and is saved as a snapshot every new thread
starts from.
"""

from managed_deepagents import define_sandbox

sandbox = define_sandbox(
    idle_ttl_seconds=1800,  # delete an idle sandbox after 30 minutes
    default_timeout=300,    # cap each shell command at 5 minutes
)
