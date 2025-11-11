import json
import os

import pytest
import pytest_filedata
import requests

import rdap


def _this_dir():
    """Returns dirname for location of this file
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
    asn_file = os.path.join(_this_dir(), "data/iana/bootstrap/asn.json")
    with open(asn_file) as fh:
        return json.load(fh)


@pytest.fixture
def rdapc():
    return rdap.RdapClient({"timeout": 10})


def pytest_addoption(parser):
    """Add custom command line options for network testing."""
    parser.addoption(
        "--network-strict",
        action="store_true",
        default=False,
        help="Run network tests in strict mode (fail on timeouts instead of skip)",
    )


def pytest_configure(config):
    """Configure pytest with network test handling."""
    config.addinivalue_line(
        "markers", "network: mark test as requiring external network access"
    )


@pytest.fixture(autouse=True)
def _network_error_handler(request, monkeypatch):
    """Auto-use fixture to handle network errors based on test markers.

    When a test is marked with @pytest.mark.network:
    - If running with -m network or --network-strict: let errors fail normally
    - Otherwise: convert timeout/connection errors to skips
    """
    # Only apply to tests marked with @pytest.mark.network
    if "network" not in [mark.name for mark in request.node.iter_markers()]:
        return

    # Check if we're in strict mode
    strict_mode = request.config.getoption("--network-strict", False) or "network" in (
        request.config.getoption("-m", "") or ""
    )

    if strict_mode:
        # In strict mode, don't modify behavior - let errors fail normally
        return

    # Not in strict mode - wrap requests.Session.get to catch network errors
    original_get = requests.Session.get

    def wrapped_get(self, url, **kwargs):
        try:
            return original_get(self, url, **kwargs)
        except (requests.exceptions.Timeout, requests.exceptions.ConnectionError) as e:
            pytest.skip(f"Network error (non-strict mode): {e}")
        except requests.exceptions.RequestException as e:
            # For other request exceptions, check if it's network-related
            if "timed out" in str(e).lower() or "connection" in str(e).lower():
                pytest.skip(f"Network error (non-strict mode): {e}")
            raise

    monkeypatch.setattr(requests.Session, "get", wrapped_get)
