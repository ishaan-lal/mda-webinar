"""The one repository Patch works on. Nothing else in the project names it.

Set PATCH_REPO in .env to point Patch at a fork. `mda deploy` forwards it to the
deployment like any other .env value.
"""

import os

REPO = os.environ.get("PATCH_REPO", "ishaan-lal/simple-game")

# Where the repo is checked out inside each thread's sandbox.
CHECKOUT = "/workspace/app"
