
from builtins import object
import re

import requests

import rdap
from rdap.config import Config
from rdap.objects import RdapAsn
from rdap.exceptions import RdapHTTPError, RdapNotFoundError


class RdapClient(object):
    """
    does RDAP queries against defined URL
    """

    def __init__(self, config=None):
        """
        config is a dict or rdap.config.Config object
        """
        if not config:
            config = dict()
        elif isinstance(config, Config):
            config = config.get("rdap")

        self.url = config.get("bootstrap_url", "https://rdap.db.ripe.net/").rstrip('/')

        # use setter
        self._recurse_roles = None
        self.recurse_roles = set(config.get("recurse_roles", ["administrative", "technical"]))

        self.headers = requests.utils.default_headers()
        self.headers["User-Agent"] = "20C-rdap/{} {}".format(rdap.__version__, self.headers["User-Agent"])

        self._asn_req = None
        self._history = []

    def _get(self, url):
        res = requests.get(url, headers=self.headers)
        for redir in res.history:
            self._history.append((redir.url, redir.status_code))
        self._history.append((res.url, res.status_code))

        if res.status_code == 200:
            return res

        msg = "RDAP lookup to {} returned {}".format(res.url, res.status_code)
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
        Sets the set of roles this will do recursive lookups for.

        Will accept any interable that can be passed to set().
        """
        self._recurse_roles = set(value)

    def get(self, query):
        """
        generic get that tries to figure out object type
        """
        qstr = query.strip().lower()
        if qstr.startswith("as"):
            return self.get_asn(qstr[2:])

        raise NotImplementedError("unknown query {}".format(query))

    def get_asn(self, asn):
        """
        get ASN object
        """
        url = "{}/autnum/{}".format(self.url, int(asn))
        # save reqest to get url for following entity lookups
        self._asn_req = self._get(url)
        return RdapAsn(self._asn_req.json(), self)

    def get_entity_data(self, handle):
        """
        get raw entity information, no need for an object
        """
        if self._asn_req:
            url = re.split("/autnum/", self._asn_req.url)[0]
        else:
            url = self.url

        url = "{}/entity/{}".format(url, handle)
        return self._get(url).json()
