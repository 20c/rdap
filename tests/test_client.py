import pytest

from rdap import client
from rdap.exceptions import RdapHTTPError


def test_strip_auth_none():
    url = "https://example.com/entity/20C"

    # test no auth
    assert url == client.strip_auth(url)


def test_strip_auth():
    url = "https://example.com/entity/20C/?key=value"

    # test no auth
    assert url == client.strip_auth(url)

    # test only auth
    assert url == client.strip_auth(url + "&apikey=12345")


def test_lacnic_bad_apikey():
    rdapc = client.RdapClient(dict(lacnic_apikey="12345"))
    with pytest.raises(RdapHTTPError) as excinfo:
        rdapc.get_asn(28001).parsed()
    assert "returned 400" in str(excinfo.value)


def test_lacnic_no_apikey(rdapc):
    assert rdapc.get_asn(28001).parsed()


def test_ignore_recurse_errors():
    rdapc = client.RdapClient(dict(lacnic_apikey="12345", ignore_recurse_errors=True))
    rdapc.get_asn(28001).parsed()
