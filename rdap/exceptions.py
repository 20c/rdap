class RdapException(Exception):
    """Base exception used by this module."""


class RdapHTTPError(RdapException):
    """An HTTP error occurred."""


class RdapNotFoundError(RdapHTTPError):
    """RDAP query returned 404 Not Found."""
