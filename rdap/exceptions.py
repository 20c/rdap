
class RdapException(Exception):
    """rdap base exception"""

class RdapNotFoundError(LookupError):
    """RDAP query returned a 404 Not Found"""
