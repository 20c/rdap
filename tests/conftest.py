
import os
import pytest

from rdap import RdapClient


pytest.setup_filedata(os.path.dirname(__file__))


def pytest_generate_tests(metafunc):
    for fixture in metafunc.fixturenames:
        if fixture.startswith('data_'):
            data = pytest.get_filedata(fixture)
            metafunc.parametrize(fixture, list(data.values()), ids=list(data.keys()))


@pytest.fixture
def rdapc():
    return RdapClient()
