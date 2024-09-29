"""Pydantic schemas for normalized RDAP data"""

import enum
import ipaddress
from datetime import datetime
from typing import Any, List, Optional, Union

import pydantic

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
    "Domain",
]


class IP_VERSION(int, enum.Enum):
    """Enum for IP version"""

    ipv4 = 4
    ipv6 = 6


class STATUS(str, enum.Enum):
    active = "active"
    inactive = "inactive"


NORMALIZED_STATUS = {
    "administrative": "active",
    "validated": "active",
}


class ROLE(str, enum.Enum):
    abuse = "abuse"
    admin = "admin"
    policy = "policy"
    technical = "technical"
    registrant = "registrant"
    billing = "billing"
    sponsor = "sponsor"


NORMALIZED_ROLES = {
    "administrative": "admin",
    "noc": "technical",
    "registrar": "registrant",
    "routing": "technical",
    "dns": "technical",
}


VALID_ROLES = [str(r) for r in ROLE]


class DNSSEC(str, enum.Enum):
    secure = "secure"
    insecure = "insecure"
    unknown = "unknown"


class GeoLocation(pydantic.BaseModel):
    """Describes geographic coordinates"""

    latitude: float
    longitude: float


class Location(pydantic.BaseModel):
    """Describes a location"""

    updated: Optional[datetime] = None
    country: Optional[str] = None
    city: Optional[str] = None
    postal_code: Optional[str] = None
    address: Optional[str] = None
    geo: Optional[GeoLocation] = None
    floor: Optional[str] = None
    suite: Optional[str] = None

    def __hash__(self):
        return f"{self.address}-{self.city}-{self.country}-{self.postal_code}-{self.floor}-{self.suite}".__hash__()


class Contact(pydantic.BaseModel):
    """Describes a point of contact"""

    created: Optional[datetime] = None
    updated: Optional[datetime] = None
    name: str
    roles: List[ROLE] = pydantic.Field(default_factory=list)
    phone: Optional[str] = None
    email: Optional[str] = None

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

        # drop any invalid roles
        data["roles"] = [
            role for role in data["roles"] if f"ROLE.{role}" in VALID_ROLES
        ]

        return data

    def __hash__(self):
        return f"{self.name}-{self.email}-{self.phone}: {self.roles}".__hash__()


class Source(pydantic.BaseModel):
    """Describes a source of rdap data

    Will contain where the data was fetched from and when
    """

    created: Optional[datetime] = None
    updated: Optional[datetime] = None
    handle: str
    urls: List[str] = pydantic.Field(default_factory=list)
    description: Optional[str] = None


class Organization(pydantic.BaseModel):
    """Describes an organization"""

    name: str


class Network(pydantic.BaseModel):
    """Describes a network"""

    created: Optional[datetime] = None
    updated: Optional[datetime] = None
    asn: int
    name: str
    organization: Organization
    locations: List[Location] = pydantic.Field(default_factory=list)
    contacts: List[Contact] = pydantic.Field(default_factory=list)
    sources: List[Source] = pydantic.Field(default_factory=list)


class IPNetwork(pydantic.BaseModel):
    """Describes an IP network"""

    created: Optional[datetime] = None
    updated: Optional[datetime] = None
    prefix: Optional[Union[ipaddress.IPv4Network, ipaddress.IPv6Network]] = None
    version: Optional[IP_VERSION] = None
    name: Optional[str] = None
    type: Optional[str] = None
    status: STATUS
    parent: Optional[Union[ipaddress.IPv4Network, ipaddress.IPv6Network]] = None
    contacts: List[Contact] = pydantic.Field(default_factory=list)
    sources: List[Source] = pydantic.Field(default_factory=list)

    @pydantic.model_validator(mode="before")
    @classmethod
    def normalize_status(cls, data: Any) -> Any:
        status = data.get("status")

        if status:
            data["status"] = NORMALIZED_STATUS.get(status, status)

        return data


class Entity(pydantic.BaseModel):
    """Describes an entity"""

    created: Optional[datetime] = None
    updated: Optional[datetime] = None
    name: str
    organization: Optional[Organization] = None
    locations: List[Location] = pydantic.Field(default_factory=list)
    contacts: List[Contact] = pydantic.Field(default_factory=list)
    sources: List[Source] = pydantic.Field(default_factory=list)


class Nameserver(pydantic.BaseModel):
    """Describes a nameserver"""

    host: str


class Domain(pydantic.BaseModel):
    """Describes a domain"""

    created: Optional[datetime] = None
    updated: Optional[datetime] = None
    name: str
    handle: str
    dns_sec: DNSSEC
    nameservers: List[Nameserver] = pydantic.Field(default_factory=list)
    contacts: List[Contact] = pydantic.Field(default_factory=list)
    sources: List[Source] = pydantic.Field(default_factory=list)
