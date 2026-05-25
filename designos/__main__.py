"""Allow ``python -m designos`` as an alias for the ``designos`` CLI.

This is a permanent fallback for environments where the user-base ``bin``
directory is not on ``PATH`` after ``pip install --user designos``.
"""

from __future__ import annotations

from designos.cli.main import app

if __name__ == "__main__":
    app()
