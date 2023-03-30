import pprint
import sys

from rdap import RdapClient


def lookup_domain(domain):
    rdapc = RdapClient()
    obj = rdapc.get_domain(domain)
    pprint.pprint(obj.data)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: get_domain.py <domain>")
        sys.exit(1)
    lookup_domain(sys.argv[1])
