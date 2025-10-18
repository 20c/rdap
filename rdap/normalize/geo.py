"""Uses googlemaps to resolve address to geolocation
and into fields
"""

import os
from datetime import datetime

import googlemaps

from rdap.context import RdapRequestState, rdap_request
from rdap.schema.normalized import GeoLocation, Location

GOOGLE_MAPS_API_KEY = os.getenv("GOOGLE_MAPS_API_KEY")


class RequestError(Exception):
    pass


class Timeout(Exception):
    pass


class NotFound(KeyError):
    pass


class GoogleKeyNotSet(Exception):
    pass


def get_client(key: str = GOOGLE_MAPS_API_KEY):
    if not key:
        raise GoogleKeyNotSet("Google Maps API Key not set")

    return googlemaps.Client(key)


def lookup(formatted_address: str, client=None) -> dict:
    """Return the latitude, longitude field values of the specified
    location.
    """
    request: RdapRequestState = rdap_request.get()

    key = f"geo:{formatted_address}"

    if key in request.entities:
        return request.entities[key]

    if not client:
        client = get_client()

    try:
        result = client.geocode(
            formatted_address,
        )
    except (
        googlemaps.exceptions.HTTPError,
        googlemaps.exceptions.ApiError,
        googlemaps.exceptions.TransportError,
    ) as exc:
        raise RequestError(exc)
    except googlemaps.exceptions.Timeout:
        raise Timeout

    if not result:
        raise NotFound

    # cache to avoid duplicate lookups during the same
    # request context
    request.entities[key] = result[0]

    return result[0]


def normalize(formatted_address: str, date: datetime = None, client=None) -> Location:
    """Takes a formatted address and returns a normalized location object"""
    try:
        result = lookup(formatted_address, client)
    except (GoogleKeyNotSet, NotFound):
        # If a google maps key is not set, return a location object with
        # only the address field set
        return Location(
            updated=date,
            address=formatted_address,
        )

    city = None
    postal_code = None
    country = None
    floor = None
    suite = None

    address_components = result.get("address_components", [])
    print("Address components:", address_components)

    for component in result.get("address_components", []):
        types = component.get("types", [])
        print("Component:", component)
        if "country" in types:
            country = component.get("short_name")

        if "postal_code" in types:
            postal_code = component.get("long_name")

        if "locality" in types or "postal_town" in types:
            city = component.get("long_name")

        if "floor" in types:
            floor = component.get("long_name")

        if "subpremise" in types:
            suite = component.get("long_name")

    return Location(
        updated=date,
        country=country,
        city=city,
        postal_code=postal_code,
        floor=floor,
        suite=suite,
        address=result.get("formatted_address"),
        geo=GeoLocation(
            latitude=result.get("geometry").get("location").get("lat"),
            longitude=result.get("geometry").get("location").get("lng"),
        ),
    )
