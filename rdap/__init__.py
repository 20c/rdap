import importlib.metadata

__version__ = importlib.metadata.version("rdap")

# client to base namespace
from rdap.client import RdapClient

# exceptions to base namespace
from rdap.exceptions import RdapBootstrapError, RdapException, RdapNotFoundError

# objects to base namespace
from rdap.objects import RdapAsn

__all__ = [
    "RdapAsn",
    "RdapBootstrapError",
    "RdapClient",
    "RdapException",
    "RdapNotFoundError",
]
