"""Durable memory across conversations, stored in Context Hub.

- agent: /memories/agent/ is shared by everyone, for facts about the repo.
- user:  /memories/user/ is private to each person, for their preferences.
  It mounts in Slack DMs and for verified Studio users. It is off in shared
  Slack channels by default, so one person's notes never leak into a group.
"""

from managed_deepagents import MemoryLayer, define_memory

memory = define_memory(
    agent=MemoryLayer(),
    user=MemoryLayer(),
)
