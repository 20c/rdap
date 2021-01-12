import pytest
import pytest_filedata

from rdap import RdapAsn, RdapNotFoundError


def assert_parsed(data, parsed):
    # dump in json format for easily adding expected
    print(
        "echo \\\n'{}'\\\n > {}/{}.expected".format(
            data.dumps(parsed), data.path, data.name
        )
    )
    assert data.expected == parsed


def test_rdap_asn_object(rdapc):
    data = dict(test="data")
    asn = RdapAsn(data, rdapc)
    assert rdapc == asn._rdapc
    assert data == asn._data


def test_rdap_asn_lookup_not_found(rdapc):
    with pytest.raises(RdapNotFoundError):
        rdapc.get_asn(65535)


def test_rdap_asn_lookup_no_client(rdapc):
    asn = rdapc.get_asn(63311)
    # force null the client
    asn._rdapc = None
    assert asn.parsed()


def test_get_rdap(rdapc):
    obj = rdapc.get_rdap("https://rdap.arin.net/registry/autnum/63311")
    assert type(obj) == RdapAsn


@pytest_filedata.RequestsData("rdap")  # XXX , real_http=True)
def test_rdap_asn_lookup(rdapc, data_rdap_autnum):
    print(data_rdap_autnum.name)
    # asn = rdap.get_asn(205726)
    asn = rdapc.get_asn(data_rdap_autnum.name)
    assert_parsed(data_rdap_autnum, asn.parsed())
