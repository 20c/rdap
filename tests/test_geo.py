from datetime import datetime
from unittest.mock import patch

import pytest

from rdap.context import RdapRequestState

# Import the functions and exceptions from your module
from rdap.normalize.geo import GoogleKeyNotSet, NotFound, normalize
from rdap.schema.normalized import GeoLocation, Location

# Mock data
MOCK_GEOCODE_RESULT = [
    {
        "formatted_address": "1600 Amphitheatre Parkway, Mountain View, CA 94043, USA",
        "geometry": {"location": {"lat": 37.4224764, "lng": -122.0842499}},
        "address_components": [
            {"types": ["country"], "short_name": "US"},
            {"types": ["postal_code"], "long_name": "94043"},
            {"types": ["locality"], "long_name": "Mountain View"},
            {"types": ["floor"], "long_name": "4"},
            {"types": ["subpremise"], "long_name": "Suite 200"},
        ],
    },
]


@pytest.fixture
def mock_google_client():
    with patch("googlemaps.Client") as mock_client:
        yield mock_client


@pytest.fixture
def mock_rdap_request():
    with patch("rdap.context.rdap_request") as mock_request:
        mock_request.get.return_value = RdapRequestState()
        yield mock_request


@pytest.fixture(autouse=True)
def mock_google_api_key():
    with patch.dict("os.environ", {"GOOGLE_MAPS_API_KEY": "fake_api_key"}):
        yield


def test_normalize_success(mock_google_client):
    mock_client = mock_google_client.return_value
    mock_client.geocode.return_value = MOCK_GEOCODE_RESULT

    date = datetime.now()

    # Mock the lookup function directly
    with patch("rdap.normalize.geo.lookup") as mock_lookup:
        # Return the first item of the list
        mock_lookup.return_value = MOCK_GEOCODE_RESULT[0]
        result = normalize("1600 Amphitheatre Parkway, Mountain View, CA", date)

    assert isinstance(result, Location)
    assert result.updated == date
    assert result.country == "US"
    assert result.city == "Mountain View"
    assert result.postal_code == "94043"
    assert result.floor == "4"
    assert result.suite == "Suite 200"
    assert result.address == "1600 Amphitheatre Parkway, Mountain View, CA 94043, USA"
    assert isinstance(result.geo, GeoLocation)
    assert result.geo.latitude == 37.4224764
    assert result.geo.longitude == -122.0842499

    # Verify that lookup was called
    mock_lookup.assert_called_once_with(
        "1600 Amphitheatre Parkway, Mountain View, CA",
        None,
    )


def test_normalize_google_key_not_set():
    with patch("rdap.normalize.geo.lookup", side_effect=GoogleKeyNotSet):
        date = datetime.now()
        result = normalize("1600 Amphitheatre Parkway, Mountain View, CA", date)

        assert isinstance(result, Location)
        assert result.updated == date
        assert result.address == "1600 Amphitheatre Parkway, Mountain View, CA"
        assert result.country is None
        assert result.city is None
        assert result.postal_code is None
        assert result.floor is None
        assert result.suite is None
        assert result.geo is None


def test_normalize_not_found():
    with patch("rdap.normalize.geo.lookup", side_effect=NotFound):
        date = datetime.now()
        result = normalize("Non-existent Address", date)

        assert isinstance(result, Location)
        assert result.updated == date
        assert result.address == "Non-existent Address"
        assert result.country is None
        assert result.city is None
        assert result.postal_code is None
        assert result.floor is None
        assert result.suite is None
        assert result.geo is None
