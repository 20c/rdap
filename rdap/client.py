import ipaddress
import json
import os
import re
import time
from functools import lru_cache
from urllib.parse import parse_qs, urlencode, urlsplit, urlunsplit

import requests

import rdap
import rdap.bootstrap
from rdap.config import Config
from rdap.exceptions import RdapHTTPError, RdapNotFoundError
from rdap.objects import RdapAsn, RdapDomain, RdapEntity, RdapNetwork


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


class RdapClient:
    """
    Client to do RDAP queries.
    """

    def __init__(self, config=None, config_dir=None):
        """
        Initialize an RdapClient.

        config is a dict or rdap.config.Config object
        config_dir is a string pointing to a config directory
        """
        if config:
            if config_dir:
                raise ValueError("Cannot pass config and config_dir")

            if isinstance(config, Config):
                self.config_dir = config.meta.get("config_dir", None)
                config = config.get("rdap")
            else:
                self.config_dir = None

        elif config_dir:
            config = Config(read=config_dir).get("rdap")
            self.config_dir = config_dir

        else:
            self.config_dir = None
            config = dict()

        self.config = config

        self.url = config.get("bootstrap_url", "https://rdap.org/").rstrip("/")
        self.self_bootstrap = config.get("self_bootstrap")

        # check for explicit bootstrap dir, otherwise set it to config_dir/bootstrap
        self.bootstrap_dir = config.get("bootstrap_dir")
        if not self.bootstrap_dir and self.config_dir:
            self.bootstrap_dir = os.path.join(self.config_dir, "bootstrap")

        # use setter
        self._recurse_roles = None
        self.recurse_roles = set(
            config.get("recurse_roles", ["administrative", "technical"])
        )

        self._asn_req = None
        self._history = []
        self._asn_tree = None
        self.timeout = config.get("timeout")

        self.http = requests.Session()
        self.http.auth = RdapRequestAuth(
            **dict(
                lacnic_apikey=config.get("lacnic_apikey", None),
            )
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

    def asn_url(self, asn):
        """Gets the correct url for specified ASN."""
        if not self.self_bootstrap:
            return self.url

        if not self._asn_tree:
            self._asn_tree = rdap.bootstrap.AsnTree(self.get_bootstrap_data("asn"))
        return self._asn_tree.get_service(asn).url

    def fetch_bootstrap_data(self, typ):
        "Fetches bootstrap data in json."
        # TODO - check modified header
        return self._get(
            self.config.get("bootstrap_data_url", "https://data.iana.org/rdap/")
            + f"{typ}.json"
        ).json()

    def get_bootstrap_data(self, typ):
        """Checks for a local cache, fetches bootstrap data and returns it."""

        try:
            data_file = os.path.join(self.bootstrap_dir, f"{typ}.json")
            cache_age = time.time() - self.config.get("bootstrap_cache_ttl") * 3600
            if os.path.getmtime(data_file) > cache_age:
                with open(data_file) as fh:
                    return json.load(fh)

        except (FileNotFoundError, TypeError):
            pass

        data = self.fetch_bootstrap_data(typ)

        # no cache if there's no bootstrap_dir
        if not self.bootstrap_dir:
            return data

        if not os.path.isdir(self.bootstrap_dir):
            os.mkdir(self.bootstrap_dir)

        with open(data_file, "w") as fh:
            json.dump(data, fh, separators=(",", ":"))
        return data

    def write_bootstrap_data(self, typ):
        """Fetches and writes bootstrap data."""

        if not self.bootstrap_dir:
            raise ValueError("bootstrap dir is not set")

        data = self.fetch_bootstrap_data(typ)

        if not os.path.isdir(self.bootstrap_dir):
            os.mkdir(self.bootstrap_dir)

        data_file = os.path.join(self.bootstrap_dir, f"{typ}.json")
        print(f"writing {data_file}")
        with open(data_file, "w") as fh:
            json.dump(data, fh, separators=(",", ":"))

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

        raise NotImplementedError(f"unknown query {query}")

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
                f"query '{url}' did not return an objectClassName"
            )
        if classname in classes:
            return classes[classname](data, self)
        else:
            raise NotImplementedError(
                f"Unknown objectClassName '{classname}' from '{url}'"
            )

    def get_asn(self, asn):
        """
        Get an ASN object.
        """
        asn = int(asn)
        url = "{}/autnum/{}".format(self.asn_url(asn), asn)
        # save reqest to get url for following entity lookups
        self._asn_req = self._get(url)
        return RdapAsn(self._asn_req.json(), self)

    def get_domain(self, domain):
        """
        Get a domain object.
        """
        url = f"{self.url}/domain/{domain}"
        return RdapAsn(self._get(url).json(), self)

    def get_ip(self, address):
        """
        Get an IP object.
        """
        url = f"{self.url}/ip/{address}"
        return RdapNetwork(self._get(url).json(), self)

    def get_entity(self, handle, base_url):
        """
        get entity information in object form
        """
        url = f"{base_url}/entity/{handle}"
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

        url = f"{url}/entity/{handle}"
        return url

    def get_data(self, url):
        """
        Get raw data and return it for when there's no need for parsing.
        """
        return self._get(url).json()
