import copy
import json
import os
from unittest.mock import patch

import pytest
import pytest_filedata

from tests.test_geo import MOCK_GEOCODE_RESULT


def dynamic_mock_address(formatted_address, client):
    result = copy.deepcopy(MOCK_GEOCODE_RESULT[0])
    result["formatted_address"] = f"{formatted_address}"
    return result


@pytest.fixture(autouse=True)
def set_google_maps_api_key():
    original_key = os.environ.get("GOOGLE_MAPS_API_KEY")
    os.environ["GOOGLE_MAPS_API_KEY"] = "your_test_api_key"
    yield
    if original_key is not None:
        os.environ["GOOGLE_MAPS_API_KEY"] = original_key
    else:
        del os.environ["GOOGLE_MAPS_API_KEY"]


@pytest_filedata.RequestsData("rdap")
def test_rdap_asn_lookup(rdapc, data_normalize_autnum):
    with patch("rdap.normalize.geo.lookup") as mock_lookup:
        mock_lookup.side_effect = dynamic_mock_address
        asn = rdapc.get_asn(data_normalize_autnum.name)
        # uncomment to write expected data
        # with open(f"tests/data/normalize/autnum/{data_normalize_autnum.name}.expected", "w") as f:
        #    f.write(json.dumps(asn.normalized, indent=2))

        assert json.dumps(data_normalize_autnum.expected, indent=2) == json.dumps(
            asn.normalized,
            indent=2,
        )


@pytest_filedata.RequestsData("rdap")
def test_rdap_entity_lookup(rdapc, data_normalize_entity):
    with patch("rdap.normalize.geo.lookup") as mock_lookup:
        mock_lookup.side_effect = dynamic_mock_address
        entity = rdapc.get_entity(data_normalize_entity.name)
        # uncomment to write expected data
        # with open(f"tests/data/normalize/entity/{data_normalize_entity.name}.expected", "w") as f:
        #    f.write(json.dumps(entity.normalized, indent=2))

        assert json.dumps(data_normalize_entity.expected, indent=2) == json.dumps(
            entity.normalized,
            indent=2,
        )


@pytest_filedata.RequestsData("rdap")
def test_rdap_domain_lookup(rdapc, data_normalize_domain):
    entity = rdapc.get_domain(data_normalize_domain.name)
    # uncomment to write expected data
    # with open(f"tests/data/normalize/domain/{data_normalize_domain.name}.expected", "w") as f:
    #    f.write(json.dumps(entity.normalized, indent=2))

    assert json.dumps(data_normalize_domain.expected, indent=2) == json.dumps(
        entity.normalized,
        indent=2,
    )


@pytest_filedata.RequestsData("rdap")
def test_rdap_ip_lookup(rdapc, data_normalize_ip):
    entity = rdapc.get_ip(data_normalize_ip.name)
    # uncomment to write expected data
    # with open(f"tests/data/normalize/ip/{data_normalize_ip.name}.expected", "w") as f:
    #    f.write(json.dumps(entity.normalized, indent=2))

    assert json.dumps(data_normalize_ip.expected, indent=2) == json.dumps(
        entity.normalized,
        indent=2,
    )
