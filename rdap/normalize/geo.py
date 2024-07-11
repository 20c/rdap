"""
Uses googlemaps to resolve address to geolocation
and into fields
"""

import os
import googlemaps

from datetime import datetime
from rdap.schema.normalized import Location, GeoLocation

GOOGLE_MAPS_API_KEY = os.getenv("GOOGLE_MAPS_API_KEY")

class RequestError(Exception):
    pass

class Timeout(Exception):
    pass

class NotFound(KeyError):
    pass

def get_client(key:str = GOOGLE_MAPS_API_KEY):
    return googlemaps.Client(key)


def lookup(formatted_address:str, client = None) -> dict:
    """
    Return the latitude, longitude field values of the specified
    location.
    """

    # TODO: cache results

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
        raise Timeout()

    if not result:
        raise NotFound()

    return result[0]

def normalize(formatted_address:str, date:datetime = None, client=None) -> Location:

    """
    Takes a formatted address and returns a normalized location object
    """

    result = lookup(formatted_address, client)

    city = None
    postal_code = None
    country = None
    floor = None
    suite = None

    for component in result.get("address_components", []):
        if "country" in component.get("types", []):
            country = component.get("short_name")
        
        if "postal_code" in component.get("types", []):
            postal_code = component.get("long_name")

        if "locality" in component.get("types", []):
            city = component.get("long_name")

        if "floor" in component.get("types", []):
            floor = component.get("long_name")

        if "subpremise" in component.get("types", []):
            suite = component.get("long_name")
         
        
    return Location(
        updated = date or datetime.now(),
        country = country,
        city = city,
        postal_code = postal_code,
        floor = floor,
        suite = suite,
        address = result.get("formatted_address"),
        geo = GeoLocation(
            latitude = result.get("geometry").get("location").get("lat"),
            longitude = result.get("geometry").get("location").get("lng")
        ),
    )