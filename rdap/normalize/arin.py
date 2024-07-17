"""
Some case specific normalization functions for ARIN data.
"""

import rdap.normalize.base as base

__all__ = [
    "Handler",
]

class Handler(base.Handler):
    """
    No known ARIN specific normalizations.
    """
    pass