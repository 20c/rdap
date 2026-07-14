class RdapException(Exception):
    """Base exception used by this module."""


class RdapHTTPError(RdapException):
    """An HTTP error occurred."""


class RdapNotFoundError(RdapHTTPError):
    """RDAP query returned 404 Not Found."""


class RdapBootstrapError(RdapNotFoundError):
    """No RDAP service could be resolved for the resource from bootstrap data.

    Raised when self-bootstrap lookup finds no service for an ASN -- i.e.
    no registry query was made at all, which is NOT the same as an authoritative
    404. A newly-assigned block can be absent from bootstrap for a while, so
    callers must not treat this as proof the resource does not exist.

    Subclass of RdapNotFoundError for backwards compatibility (existing
    ``except RdapNotFoundError`` handlers still catch it); catch this first to
    distinguish "never queried" from "registry said no".
    """


class RIRAssignmentError(RdapException):
    """RIR delegated-stats data could not be fetched or is incomplete/corrupt.

    Raised instead of caching/loading a bad file, since consumers treat an
    absent ASN as 'unassigned' -- a truncated file would make live ASNs look
    reclaimed.
    """
