"""
Some case specific normalization functions for LACNIC data.
"""

import rdap.normalize.base as base

__all__ = [
    "Handler",
]

class Handler(base.Handler):
    """
    No known LACNIC specific normalizations.
    """
    pass