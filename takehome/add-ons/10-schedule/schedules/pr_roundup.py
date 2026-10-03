"""A weekday roundup of your fork's open PRs, posted to Slack.

The file name (`pr_roundup`) is the schedule's name. MDA reads this file at
compile time WITHOUT running it, so every value must be a literal: no env
vars, no function calls, no f-strings.
"""

from managed_deepagents import define_schedule

schedule = define_schedule(
    # When to run, as a 5-field cron: minute hour day month weekday. This is
    # 9:03am on weekdays. To watch it fire while testing, set it a few minutes
    # ahead, redeploy, then set it back.
    cron="3 9 * * 1-5",
    timezone="America/Los_Angeles",
    prompt=(
        "List this repository's open pull requests with github__list_pull_requests. "
        "Reply with one line per PR: title, link, and days open. Flag any open "
        "more than 3 days. If there are none, say so in one line. Do not change "
        "any code."
    ),
    deliver_to={
        "channel": "slack",
        # TODO(step 10): the ID of a Slack channel to post in. Make your own
        # channel, like #patch-ada, invite your bot to it, then copy the ID
        # from the channel's details (About > Channel ID, starts with C).
        "to": {"type": "provider_conversation", "conversation_id": "TODO"},
    },
)
