import json
import os

import pytest
import pytest_filedata

import rdap


def _this_dir():
    """
    returns dirname for location of this file
    py.test no longer allows fixtures to be called
    directly so we provide a private function that can be
    """
    return os.path.dirname(__file__)


@pytest.fixture
def this_dir():
    return _this_dir()


pytest_filedata.setup(_this_dir())


def pytest_generate_tests(metafunc):
    for fixture in metafunc.fixturenames:
        if fixture.startswith("data_"):
            data = pytest_filedata.get_data(fixture)
            metafunc.parametrize(fixture, list(data.values()), ids=list(data.keys()))


@pytest.fixture
def iana_asn():
    asn_file = os.path.join(_this_dir(), "data/iana/asn.json")
    with open(asn_file) as fh:
        data = json.load(fh)
        return data


@pytest.fixture
def rdapc():
    return rdap.RdapClient({"timeout": 10})
