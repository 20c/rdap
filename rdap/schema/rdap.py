from datetime import datetime
from typing import Dict, List, Optional, Union

from pydantic import BaseModel, Field

__all__ = [
    "Link",
    "Event",
    "Notice",
    "VCardValue",
    "Remark",
    "Entity",
    "IPNetwork",
]


class Link(BaseModel):
    """Represents a hyperlink in the RDAP response."""

    # The label or description of the link
    value: Optional[str] = None
    # The relationship of the link to the current object
    rel: Optional[str] = None
    # The MIME type of the target resource
    type: Optional[str] = None
    # The URL of the link
    href: Optional[str] = None


class Event(BaseModel):
    """Represents a timestamped event in the lifecycle of an RDAP object."""

    # The type of event (e.g., "registration", "last changed")
    eventAction: Optional[str] = None
    # The date and time of the event
    eventDate: Optional[datetime] = None


class Notice(BaseModel):
    """Represents a notice or message in the RDAP response."""

    # The title of the notice
    title: Optional[str] = None
    # A list of text lines comprising the notice
    description: List[str] = Field(default_factory=list)
    # Optional links related to the notice
    links: List[Link] = Field(default_factory=list)


class VCardValue(BaseModel):
    """Represents additional properties for vCard values."""

    # Types associated with the vCard value (e.g., "work", "voice" for telephone)
    type: Optional[List[str]] = None


class Remark(BaseModel):
    """Represents a remark or comment in the RDAP response."""

    # The title of the remark
    title: Optional[str] = None
    # A list of text lines comprising the remark
    description: List[str] = Field(default_factory=list)


class Entity(BaseModel):
    """Represents an entity (organization, individual, or role) in the RDAP response."""

    # A unique identifier for the entity
    handle: str = Field(default_factory=str)
    # Contact information in vCard format
    vcardArray: List[Union[str, List[List[Union[str, dict, list, None]]]]] = Field(
        default_factory=list,
    )
    # Roles of the entity (e.g., registrant, technical, administrative)
    roles: List[str] = Field(default_factory=list)
    # Links related to the entity
    links: List[Link] = Field(default_factory=list)
    # Events associated with the entity
    events: List[Event] = Field(default_factory=list)
    # Status of the entity
    status: List[str] = Field(default_factory=list)
    # WHOIS server for the entity
    port43: str = Field(default_factory=str)
    # Type of the object (always "entity" for Entity)
    objectClassName: str
    # Additional remarks about the entity
    remarks: List[Remark] = Field(default_factory=list)
    # Nested entities (e.g., contacts within an organization)
    entities: List["Entity"] = Field(default_factory=list)

    @property
    def self_link(self) -> Optional[str]:
        """Returns the href of the link where rel == 'self'"""
        for link in self.links:
            if link.rel == "self":
                return link.href
        return None


class IPNetwork(BaseModel):
    """Represents an IP network in the RDAP response."""

    # list of conformance levels
    rdapConformance: List[str] = Field(default_factory=list)
    # Notices related to the IP network
    notices: List[Notice] = Field(default_factory=list)
    # A unique identifier for the IP network
    handle: Optional[str] = None
    # The first IP address in the network range
    startAddress: Optional[str] = None
    # The last IP address in the network range
    endAddress: Optional[str] = None
    # IP version (v4 or v6)
    ipVersion: Optional[str] = None
    # Name of the network
    name: Optional[str] = None
    # Type of the network allocation
    type: Optional[str] = None
    # Handle of the parent network
    parentHandle: Optional[str] = None
    # Additional remarks about the network
    remarks: List[Remark] = Field(default_factory=list)
    # Events associated with the network
    events: List[Event] = Field(default_factory=list)
    # Links related to the network
    links: List[Link] = Field(default_factory=list)
    # Entities associated with the network
    entities: List[Entity] = Field(default_factory=list)
    # WHOIS server for the network
    port43: Optional[str] = None
    # Status of the network
    status: List[str] = Field(default_factory=list)
    # Type of the object (always "ip network" for IPNetwork)
    objectClassName: Optional[str] = None
    # CIDR notation for the network
    cidr0_cidrs: List[Dict] = Field(default_factory=list)
    # Origin AS numbers for the network
    arin_originas0_originautnums: List = Field(default_factory=list)


class DSData(BaseModel):
    """Represents DS data for secure DNS in the RDAP response."""

    # Key tag for the DS record
    keyTag: Optional[int] = None
    # Algorithm number for the DS record
    algorithm: Optional[int] = None
    # Digest type for the DS record
    digestType: Optional[int] = None
    # Digest value for the DS record
    digest: Optional[str] = None


class SecureDNS(BaseModel):
    # true if there are DS records in the parent, false otherwise.
    delegationSigned: Optional[bool] = None
    # if the zone has been signed, false otherwise.
    zeroSigned: Optional[bool] = None
    # DS data for secure DNS
    dsData: List[DSData] = Field(default_factory=list)


class Nameserver(BaseModel):
    objectClassName: Optional[str] = None
    ldhName: Optional[str] = None
    unicodeName: Optional[str] = None
    ipAddresses: Dict[str, List[str]] = Field(default_factory=dict)
    remarks: List[Remark] = Field(default_factory=list)
    port43: Optional[str] = None
    events: List[Event] = Field(default_factory=list)


class Domain(BaseModel):
    """Represents a domain name in the RDAP response."""

    # list of conformance levels
    rdapConformance: List[str] = Field(default_factory=list)
    # Notices related to the domain
    notices: List[Notice] = Field(default_factory=list)
    # A unique identifier for the domain
    handle: Optional[str] = None
    # The domain name in LDH (Letter Digit Hyphen) format
    ldhName: Optional[str] = None
    # Events associated with the domain
    events: List[Event] = Field(default_factory=list)
    # Links related to the domain
    links: List[Link] = Field(default_factory=list)
    # Entities associated with the domain
    entities: List[Entity] = Field(default_factory=list)
    # WHOIS server for the domain
    port43: str = Field(default_factory=str)
    # Network information for the domain
    network: Optional[IPNetwork] = None
    # Type of the object (always "domain" for Domain)
    objectClassName: Optional[str] = None

    secureDNS: Optional[SecureDNS] = None

    nameservers: List[Nameserver] = Field(default_factory=list)


class AutNum(BaseModel):
    """Represents an Autonomous System Number in the RDAP response."""

    # list of conformance levels
    rdapConformance: List[str] = Field(default_factory=list)
    # Notices related to the AS number
    notices: List[Notice] = Field(default_factory=list)
    # A unique identifier for the AS number
    handle: Optional[str] = None
    # The starting AS number in the range
    startAutnum: Optional[int] = None
    # The ending AS number in the range (same as startAutnum for single AS)
    endAutnum: Optional[int] = None
    # Name of the AS
    name: Optional[str] = None
    # WHOIS server for the AS number
    port43: Optional[str] = None

    # Type of the object (always "autnum" for AutNum)
    objectClassName: Optional[str] = None

    # Events associated with the AS number
    events: List[Event] = Field(default_factory=list)
    # Links related to the AS number
    links: List[Link] = Field(default_factory=list)
    # Entities associated with the AS number
    entities: List[Entity] = Field(default_factory=list)
    # Status of the AS number
    status: List[str] = Field(default_factory=list)

    # Remarks about the AS number
    remarks: List[Remark] = Field(default_factory=list)


Entity.model_rebuild()
