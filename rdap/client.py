from __future__ import absolute_import, division, print_function
from builtins import object, str
import re

# import for either Python 2 or 3
try:
    from urllib.parse import parse_qs, urlencode, urlsplit, urlunsplit
except ImportError:
    from urllib.parse import parse_qs, urlsplit, urlunsplit
    from urllib.parse import urlencode

import ipaddress
from functools import lru_cache

import requests

import rdap
from rdap.config import Config
from rdap.objects import RdapAsn, RdapObject, RdapNetwork, RdapDomain, RdapEntity
from rdap.exceptions import RdapHTTPError, RdapNotFoundError


class RdapRequestAuth(requests.auth.AuthBase):
    """
    Adds authentication to HTTP RDAP Request objects.

    Currently only supports LACNIC's APIKEY
    """

    def __init__(self, lacnic_apikey=None):
        self.lacnic_apikey = lacnic_apikey

        self.has_auth = False
        if lacnic_apikey:
            self.has_auth = True

    def __call__(self, request):
        # update history?

        if not self.has_auth:
            return request

        # apikeys, quick and dirty until other RIRs support them
        # checks scheme as well since API keys shouldn't be sent over http
        if request.url.startswith("https://rdap.lacnic.net/"):
            params = dict(apikey=self.lacnic_apikey)
            request.prepare_url(request.url, params)

        return request


def strip_auth(url):
    """
    Strip any sensitive auth information out of the URL.
    """
    parsed = urlsplit(url)
    if not parsed.query:
        return url

    params = parse_qs(parsed.query)

    # LACNIC
    if "apikey" in params:
        del params["apikey"]
        parts = list(parsed)
        # overwrite query, use str() since py2 returns a newstr
        parts[3] = str(urlencode(params, doseq=True))
        return urlunsplit(parts)

    return url


class RdapClient(object):
    """
    Client to do RDAP queries against defined bootstrap URL.
    """

    def __init__(self, config=None):
        """
        config is a dict or rdap.config.Config object
        """
        if not config:
            config = dict()
        elif isinstance(config, Config):
            config = config.get("rdap")

        self.url = config.get("bootstrap_url", "https://rdap.org/").rstrip("/")

        # use setter
        self._recurse_roles = None
        self.recurse_roles = set(
            config.get("recurse_roles", ["administrative", "technical"])
        )

        self._asn_req = None
        self._history = []
        self.timeout = config.get("timeout", 0.5)

        self.http = requests.Session()
        self.http.auth = RdapRequestAuth(
            **dict(lacnic_apikey=config.get("lacnic_apikey", None),)
        )

        self.http.headers["User-Agent"] = "20C-rdap/{} {}".format(
            rdap.__version__, self.http.headers["User-Agent"]
        )

    def _get(self, url):
        res = self.http.get(url, timeout=self.timeout)
        for redir in res.history:
            self._history.append((strip_auth(redir.url), redir.status_code))
        self._history.append((strip_auth(res.url), res.status_code))

        if res.status_code == 200:
            return res

        msg = "RDAP lookup to {} returned {}".format(
            strip_auth(res.url), res.status_code
        )
        if res.status_code == 404:
            raise RdapNotFoundError(msg)
        raise RdapHTTPError(msg)

    @property
    def history(self):
        return self._history

    @property
    def recurse_roles(self):
        """Gets the set of roles this will do recursive lookups for."""
        return self._recurse_roles

    @recurse_roles.setter
    def recurse_roles(self, value):
        """
        Sets the set of roles this client will do recursive lookups for.

        Will accept any interable that can be passed to set().
        """
        self._recurse_roles = set(value)

    def get(self, query):
        """
        Generic get that tries to figure out object type and returns an object.
        """
        qstr = query.strip().lower()

        # ASN
        if qstr.startswith("as"):
            return self.get_asn(qstr[2:])

        # IP address
        try:
            address = ipaddress.ip_interface(str(qstr))
            return self.get_ip(address.ip)

        except ValueError:
            pass

        # domain
        if "." in qstr:
            return self.get_domain(qstr)

        raise NotImplementedError("unknown query {}".format(query))

    @lru_cache(maxsize=1024)
    def get_rdap(self, url):
        """
        Get RDAP information from an full RDAP url and returns an object

        Note: this relies on objectClassName which not all RDAP registries support.
        """
        data = self._get(url).json()
        classes = {
            "autnum": RdapAsn,
            "domain": RdapDomain,
            "entity": RdapEntity,
            "ip network": RdapNetwork,
        }

        classname = data.get("objectClassName", None)
        if not classname:
            raise NotImplementedError(
                "query '{}' did not return an objectClassName".format(url)
            )
        if classname in classes:
            return classes[classname](data, self)
        else:
            raise NotImplementedError(
                "Unknown objectClassName '{}' from '{}'".format(classname, url)
            )

    def get_asn(self, asn):
        """
        Get an ASN object.
        """
        url = "{}/autnum/{}".format(self.url, int(asn))
        # save reqest to get url for following entity lookups
        self._asn_req = self._get(url)
        return RdapAsn(self._asn_req.json(), self)

    def get_domain(self, domain):
        """
        Get a domain object.
        """
        url = "{}/domain/{}".format(self.url, domain)
        return RdapAsn(self._get(url).json(), self)

    def get_ip(self, address):
        """
        Get an IP object.
        """
        url = "{}/ip/{}".format(self.url, address)
        return RdapNetwork(self._get(url).json(), self)

    def get_entity(self, handle, base_url):
        """
        get entity information in object form
        """
        url = "{}/entity/{}".format(base_url, handle)
        return RdapEntity(self._get(url).json(), self)

    def get_entity_url(self, handle):
        """
        Get entity url for handle.

        This fucntion must be able to handle doing recursive lookups to the current URL after a bootstrap redirect for registries that don't link 'self'
        """
        if self._asn_req:
            url = re.split("/autnum/", self._asn_req.url)[0]
        else:
            url = self.url

        url = "{}/entity/{}".format(url, handle)
        return url

    def get_data(self, url):
        """
        Get raw data and return it for when there's no need for parsing.
        """
        return self._get(url).json()
