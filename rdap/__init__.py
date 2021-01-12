from pkg_resources import get_distribution

__version__ = get_distribution("rdap").version

# client to base namespace
from rdap.client import RdapClient

# exceptions to base namespace
from rdap.exceptions import RdapException, RdapNotFoundError

# objects to base namespace
from rdap.objects import RdapAsn
