"""Conftest for factory tests.

Adds the factory root to sys.path so factory tools can use absolute imports
(``import _kernel_bridge``, ``from archetypes import ...``). The repo root
is also added so factory code can ``import kernel.*``.

The leading-dot in ``.factory`` prevents normal package imports, so absolute
imports + sys.path manipulation is the simplest path.

CRITICAL: Repo root must be FIRST in sys.path to override any installed
kernel package in site-packages. Factory tests must use the local kernel.
"""

from __future__ import annotations

import sys
from pathlib import Path

_REPO_ROOT: Path = Path(__file__).resolve().parents[2]
_FACTORY_ROOT: Path = Path(__file__).resolve().parents[1]

# CRITICAL: Insert repo root FIRST to override site-packages kernel
for entry in (_REPO_ROOT, _FACTORY_ROOT):
    s = str(entry)
    # Remove if already present (might be at wrong position)
    if s in sys.path:
        sys.path.remove(s)
    # Insert at position 0 (highest priority)
    sys.path.insert(0, s)
