class RdapException(Exception):
    """Base exception used by this module."""


class RdapHTTPError(RdapException):
    """An HTTP error occurred."""


class RdapNotFoundError(RdapHTTPError):
    """RDAP query returned 404 Not Found."""


class RIRAssignmentError(RdapException):
    """RIR delegated-stats data could not be fetched or is incomplete/corrupt.

    Raised instead of caching/loading a bad file, since consumers treat an
    absent ASN as 'unassigned' -- a truncated file would make live ASNs look
    reclaimed.
    """
