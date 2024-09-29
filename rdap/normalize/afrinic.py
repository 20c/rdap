"""Some case specific normalization functions for AFRINIC data."""

from rdap.normalize import base

__all__ = [
    "Handler",
]


class Handler(base.Handler):
    """No known AFRINIC specific normalizations."""
