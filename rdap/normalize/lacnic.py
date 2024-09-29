"""Some case specific normalization functions for LACNIC data."""

from rdap.normalize import base

__all__ = [
    "Handler",
]


class Handler(base.Handler):
    """No known LACNIC specific normalizations."""
