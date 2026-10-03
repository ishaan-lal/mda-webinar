"""Slack: DM your Patch, or @mention it in a channel. Set up by `mda deploy`.

No Slack app to create and no tokens in .env. On the first deploy, the CLI
prints an authorization link: pick the webinar Slack workspace and approve.
After that, the bot DMs you. Files dropped in a thread land in the sandbox
under /workspace/attachments/, and the agent sends files back with
`attach_file`.
"""

from managed_deepagents import channels

channel = channels.slack(
    # TODO(step 9): everyone in the webinar workspace has a Patch, so make
    # yours findable: "Patch-<your name>", like "Patch-Ada". Use 1-35
    # characters: letters, numbers, spaces, underscores, dashes, or periods
    # (no parentheses).
    name="TODO",
    # TODO(step 9): what your Patch does, in up to 139 characters.
    description="TODO",
    background_color="#1C3C3C",
)
