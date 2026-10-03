"""My Patch: fixes bugs and builds small features in my fork of simple-game.

This is the only required file in a Managed Deep Agent project. Most features
turn on when you add a file to the project, not by changing this one. You'll
come back here in steps 3 and 6 to wire things up.
"""

from managed_deepagents import define_deep_agent

agent = define_deep_agent(
    # TODO(step 1): name your agent: letters, numbers, underscores, or hyphens,
    # starting with a letter. It becomes your deployment's name in LangSmith.
    name="TODO",
    model="anthropic:claude-sonnet-5",
    # TODO(step 3): wire in the middleware (import it at the top, too).
    # TODO(step 6): pause before a pull request opens, with interrupt_on.
)
