"""Slack: DM Patch or @mention it in a channel. Set up by `mda deploy`.

No Slack app to create and no tokens in .env. On first deploy the CLI prints an
authorization link, and after that the bot DMs you. Files dropped in the thread
land in the sandbox under /workspace/attachments/, and the agent can send files
back with `attach_file`.
"""

from managed_deepagents import channels

channel = channels.slack(
    name="Patch",
    description="Fixes bugs and builds small features in the Tetris game, then opens a PR.",
    background_color="#1C3C3C",
)
