from pkg_resources import get_distribution


__version__ = get_distribution("rdap").version

# objects to base namespace
from rdap.objects import RdapAsn

# exceptions to base namespace
from rdap.exceptions import RdapException, RdapNotFoundError

# client to base namespace
from rdap.client import RdapClient
