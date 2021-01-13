import os
import shutil

import pytest

import rdap
from rdap import bootstrap


def check_asn_service(asn, service):
    assert asn >= service.start_asn
    assert asn <= service.end_asn
    assert service.url


def test_asn_tree(iana_asn):
    tree = bootstrap.AsnTree(iana_asn)
    empty_tree = bootstrap.AsnTree()
    empty_tree.load_data(iana_asn)
    assert len(empty_tree) == len(tree)


@pytest.mark.parametrize("asn", [1, 1876, 1877, 2403, 63311, 400284, 400285, 401308])
def test_asn_tree_lookup(iana_asn, asn):
    tree = bootstrap.AsnTree(iana_asn)
    check_asn_service(asn, tree.get_service(asn))


@pytest.mark.parametrize("asn", [0, 65535, 99999999])
def test_asn_tree_lookup_notfound(iana_asn, asn):
    tree = bootstrap.AsnTree(iana_asn)
    with pytest.raises(LookupError):
        check_asn_service(asn, tree.get_service(asn))


@pytest.mark.parametrize("asn", [63311])
def test_asn_lookup(this_dir, asn, tmpdir):
    config_dir = os.path.join(this_dir, "data", "iana")
    shutil.copy(os.path.join(config_dir, "config.yml"), tmpdir)

    # check download and cache
    rdapc = rdap.RdapClient(config_dir=tmpdir)
    rdapc.get_asn(asn)
    assert rdapc.history[0][0] == "https://data.iana.org/rdap/asn.json"

    # delete history and get again to test lookup caching
    rdapc._history = []
    rdapc.get_asn(asn)
    print(rdapc.history)
    assert rdapc.history[0][0] != "https://data.iana.org/rdap/asn.json"
    assert 1 == len(rdapc.history)

    asn_db_file = os.path.join(tmpdir, "bootstrap", "asn.json")
    assert os.path.isfile(asn_db_file)
    # delete cache and manually write file
    os.remove(os.path.join(tmpdir, "bootstrap", "asn.json"))
    assert not os.path.isfile(asn_db_file)

    rdapc.write_bootstrap_data("asn")
    assert os.path.isfile(asn_db_file)

    rdapc._history = []
    rdapc.get_asn(asn)
    print(rdapc.history)
    assert rdapc.history[0][0] != "https://data.iana.org/rdap/asn.json"
    assert 1 == len(rdapc.history)


@pytest.mark.parametrize("asn", [63311])
def test_asn_bootstrap_cache(tmpdir, asn):
    config = dict(
        self_bootstrap=True,
        bootstrap_dir=tmpdir,
    )
    asn_db_file = os.path.join(tmpdir, "asn.json")

    # check download and cache
    rdapc = rdap.RdapClient(config)
    rdapc.get_asn(asn)
    assert os.path.isfile(asn_db_file)
    assert rdapc.history[0][0] == "https://data.iana.org/rdap/asn.json"

    # delete history and get again to test lookup caching
    rdapc._history = []
    rdapc.get_asn(asn)
    print(rdapc.history)
    assert rdapc.history[0][0] != "https://data.iana.org/rdap/asn.json"
    assert 1 == len(rdapc.history)

    # delete cache and manually write file
    os.remove(asn_db_file)
    assert not os.path.isfile(asn_db_file)

    rdapc.write_bootstrap_data("asn")
    assert os.path.isfile(asn_db_file)

    rdapc._history = []
    rdapc.get_asn(asn)
    print(rdapc.history)
    assert rdapc.history[0][0] != "https://data.iana.org/rdap/asn.json"
    assert 1 == len(rdapc.history)


@pytest.mark.parametrize("asn", [63311])
def test_asn_bootstrap_no_cache(asn):
    config = dict(
        self_bootstrap=True,
    )

    # check download and cache
    rdapc = rdap.RdapClient(config)
    rdapc.get_asn(asn)
    assert rdapc.history[0][0] == "https://data.iana.org/rdap/asn.json"
