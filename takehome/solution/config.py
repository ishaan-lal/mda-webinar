"""The one repository Patch works on: your fork, from PATCH_REPO in .env.

Nothing else in the project names it. The agent reads it back from the
checkout's git remote, and `mda deploy` forwards PATCH_REPO to the deployment.
"""

import os

REPO = os.environ.get("PATCH_REPO", "").strip()

# Where the repo is checked out inside each thread's sandbox.
CHECKOUT = "/workspace/app"
