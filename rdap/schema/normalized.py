"""
Pydantic schemas for normalized RDAP data
"""

from datetime import datetime
from typing import Any
import pydantic
import enum
import ipaddress

__all__ = [
    "IP_VERSION",
    "STATUS",
    "ROLE",
    "DNSSEC",
    "GeoLocation",
    "Location",
    "Contact",
    "Source",
    "Organization",
    "Network",
    "IPNetwork",
    "Entity",
    "Nameserver",
    "Domain"
]

class IP_VERSION(int, enum.Enum):
    """
    Enum for IP version
    """
    ipv4 = 4
    ipv6 = 6

class STATUS(str, enum.Enum):
    active = "active"
    inactive = "inactive"

class ROLE(str, enum.Enum):
    abuse = "abuse"
    admin = "admin"
    policy = "policy"
    technical = "technical"
    registrant = "registrant"

NORMALIZED_ROLES = {
    "administrative": "admin",
    "noc": "technical",
    "registrar": "registrant"
}

class DNSSEC(str, enum.Enum):
    secure = "secure"
    insecure = "insecure"
    unknown = "unknown"

class GeoLocation(pydantic.BaseModel):
    """
    Describes geographic coordinates
    """
    latitude: float
    longitude: float

class Location(pydantic.BaseModel):
    """
    Describes a location
    """
    updated: datetime | None = None
    country: str | None = None
    city: str | None = None
    postal_code: str | None = None
    address: str | None = None
    geo: GeoLocation | None = None
    floor: str | None = None
    suite: str | None = None

class Contact(pydantic.BaseModel):
    """
    Describes a point of contact
    """
    #created: datetime | None = None
    #updated: datetime | None = None
    name: str
    roles: list[ROLE] = pydantic.Field(default_factory=list)
    phone: str | None = None
    email: str | None = None

    @pydantic.model_validator(mode="before")
    @classmethod
    def normalize_roles(cls, data: Any) -> Any:
        
        roles = []

        for role in data.get("roles", []):
            role = NORMALIZED_ROLES.get(role, role)
            roles.append(role)
        
        data["roles"] = roles

        # drop duplicates

        data["roles"] = list(set(data["roles"]))

        return data


    def __hash__(self):
        return f"{self.name}-{self.email}-{self.phone}: {self.roles}".__hash__()

class Source(pydantic.BaseModel):
    """
    Describes a source of rdap data

    Will contain where the data was fetched from and when
    """
    created: datetime | None = None
    updated: datetime | None = None
    handle: str
    urls: list[str] = pydantic.Field(default_factory=list)
    description: str | None = None


class Organization(pydantic.BaseModel):
    """
    Describes an organization
    """
    name: str

class Network(pydantic.BaseModel):
    """
    Describes a network
    """
    created: datetime | None = None
    updated: datetime | None = None
    asn: int
    name: str
    organization: Organization
    location: Location | None = None
    contacts: list[Contact] = pydantic.Field(default_factory=list)
    sources: list[Source] = pydantic.Field(default_factory=list)


class IPNetwork(pydantic.BaseModel):
    """
    Describes an IP network
    """
    created: datetime | None = None
    updated: datetime | None = None
    prefix: ipaddress.IPv4Network | ipaddress.IPv6Network | None = None
    version: IP_VERSION | None = None
    name: str
    type: str
    status: STATUS
    parent: ipaddress.IPv4Network | ipaddress.IPv6Network | None = None
    contacts: list[Contact] = pydantic.Field(default_factory=list)
    sources: list[Source] = pydantic.Field(default_factory=list)

class Entity(pydantic.BaseModel):
    """
    Describes an entity
    """
    created: datetime | None = None
    updated: datetime | None = None
    name: str
    organization: Organization | None = None
    location: Location | None = None
    contacts: list[Contact] = pydantic.Field(default_factory=list)
    sources: list[Source] = pydantic.Field(default_factory=list)

class Nameserver(pydantic.BaseModel):
    """
    Describes a nameserver
    """
    host: str

class Domain(pydantic.BaseModel):
    """
    Describes a domain
    """
    created: datetime | None = None
    updated: datetime | None = None
    name: str
    handle: str
    dns_sec: DNSSEC
    nameservers: list[Nameserver] = pydantic.Field(default_factory=list)
    contacts: list[Contact] = pydantic.Field(default_factory=list)
    sources: list[Source] = pydantic.Field(default_factory=list)