
from builtins import object
import re

import requests

import rdap
from rdap.config import Config
from rdap.objects import RdapAsn
from rdap.exceptions import RdapNotFoundError


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

        self.headers = requests.utils.default_headers()
        self.headers["User-Agent"] = "rdap/{} {}".format(rdap.__version__, self.headers["User-Agent"])

        self._asn_req = None
        self._history = []

    def _get(self, url):
        res = requests.get(url, headers=self.headers)
        for redir in res.history:
            self._history.append((redir.url, redir.status_code))
        self._history.append((res.url, res.status_code))

        if res.status_code == 200:
            return res
        elif res.status_code == 404:
            raise RdapNotFoundError()

        raise RuntimeError("status for {} was {}".format(res.url, res.status_code))

    @property
    def history(self):
        return self._history

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
