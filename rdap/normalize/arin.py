"""Some case specific normalization functions for ARIN data."""

from rdap.normalize import base

__all__ = [
    "Handler",
]


class Handler(base.Handler):
    """No known ARIN specific normalizations."""
