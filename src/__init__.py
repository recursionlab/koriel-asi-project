"""Top-level package for the Koriel ASI project.

This file allows the modules located in ``src/`` to be imported as a
package after installation (e.g. ``from src import ab``).
"""

# Package exports are intentionally minimal to avoid importing heavy
# dependencies at module import time. Submodules can be imported as
# ``from src import ab`` or ``from src import rcc`` after installation.

__all__: list[str] = []
