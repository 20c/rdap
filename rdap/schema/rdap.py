from datetime import datetime

from pydantic import BaseModel, Field

__all__ = [
    "Entity",
    "Event",
    "IPNetwork",
    "Link",
    "Notice",
    "Remark",
    "VCardValue",
]


class Link(BaseModel):
    """Represents a hyperlink in the RDAP response."""

    # The label or description of the link
    value: str | None = None
    # The relationship of the link to the current object
    rel: str | None = None
    # The MIME type of the target resource
    type: str | None = None
    # The URL of the link
    href: str | None = None


class Event(BaseModel):
    """Represents a timestamped event in the lifecycle of an RDAP object."""

    # The type of event (e.g., "registration", "last changed")
    eventAction: str | None = None
    # The date and time of the event
    eventDate: datetime | None = None


class Notice(BaseModel):
    """Represents a notice or message in the RDAP response."""

    # The title of the notice
    title: str | None = None
    # A list of text lines comprising the notice
    description: list[str] = Field(default_factory=list)
    # Optional links related to the notice
    links: list[Link] = Field(default_factory=list)


class VCardValue(BaseModel):
    """Represents additional properties for vCard values."""

    # Types associated with the vCard value (e.g., "work", "voice" for telephone)
    type: list[str] | None = None


class Remark(BaseModel):
    """Represents a remark or comment in the RDAP response."""

    # The title of the remark
    title: str | None = None
    # A list of text lines comprising the remark
    description: list[str] = Field(default_factory=list)


class Entity(BaseModel):
    """Represents an entity (organization, individual, or role) in the RDAP response."""

    # A unique identifier for the entity
    handle: str = Field(default_factory=str)
    # Contact information in vCard format
    vcardArray: list[str | list[list[str | dict | list | None]]] = Field(
        default_factory=list,
    )
    # Roles of the entity (e.g., registrant, technical, administrative)
    roles: list[str] = Field(default_factory=list)
    # Links related to the entity
    links: list[Link] = Field(default_factory=list)
    # Events associated with the entity
    events: list[Event] = Field(default_factory=list)
    # Status of the entity
    status: list[str] = Field(default_factory=list)
    # WHOIS server for the entity
    port43: str = Field(default_factory=str)
    # Type of the object (always "entity" for Entity)
    objectClassName: str
    # Additional remarks about the entity
    remarks: list[Remark] = Field(default_factory=list)
    # Nested entities (e.g., contacts within an organization)
    entities: list["Entity"] = Field(default_factory=list)

    @property
    def self_link(self) -> str | None:
        """Returns the href of the link where rel == 'self'"""
        for link in self.links:
            if link.rel == "self":
                return link.href
        return None


class IPNetwork(BaseModel):
    """Represents an IP network in the RDAP response."""

    # list of conformance levels
    rdapConformance: list[str] = Field(default_factory=list)
    # Notices related to the IP network
    notices: list[Notice] = Field(default_factory=list)
    # A unique identifier for the IP network
    handle: str | None = None
    # The first IP address in the network range
    startAddress: str | None = None
    # The last IP address in the network range
    endAddress: str | None = None
    # IP version (v4 or v6)
    ipVersion: str | None = None
    # Name of the network
    name: str | None = None
    # Type of the network allocation
    type: str | None = None
    # Handle of the parent network
    parentHandle: str | None = None
    # Additional remarks about the network
    remarks: list[Remark] = Field(default_factory=list)
    # Events associated with the network
    events: list[Event] = Field(default_factory=list)
    # Links related to the network
    links: list[Link] = Field(default_factory=list)
    # Entities associated with the network
    entities: list[Entity] = Field(default_factory=list)
    # WHOIS server for the network
    port43: str | None = None
    # Status of the network
    status: list[str] = Field(default_factory=list)
    # Type of the object (always "ip network" for IPNetwork)
    objectClassName: str | None = None
    # CIDR notation for the network
    cidr0_cidrs: list[dict] = Field(default_factory=list)
    # Origin AS numbers for the network
    arin_originas0_originautnums: list = Field(default_factory=list)


class DSData(BaseModel):
    """Represents DS data for secure DNS in the RDAP response."""

    # Key tag for the DS record
    keyTag: int | None = None
    # Algorithm number for the DS record
    algorithm: int | None = None
    # Digest type for the DS record
    digestType: int | None = None
    # Digest value for the DS record
    digest: str | None = None


class SecureDNS(BaseModel):
    # true if there are DS records in the parent, false otherwise.
    delegationSigned: bool | None = None
    # if the zone has been signed, false otherwise.
    zeroSigned: bool | None = None
    # DS data for secure DNS
    dsData: list[DSData] = Field(default_factory=list)


class Nameserver(BaseModel):
    objectClassName: str | None = None
    ldhName: str | None = None
    unicodeName: str | None = None
    ipAddresses: dict[str, list[str]] = Field(default_factory=dict)
    remarks: list[Remark] = Field(default_factory=list)
    port43: str | None = None
    events: list[Event] = Field(default_factory=list)


class Domain(BaseModel):
    """Represents a domain name in the RDAP response."""

    # list of conformance levels
    rdapConformance: list[str] = Field(default_factory=list)
    # Notices related to the domain
    notices: list[Notice] = Field(default_factory=list)
    # A unique identifier for the domain
    handle: str | None = None
    # The domain name in LDH (Letter Digit Hyphen) format
    ldhName: str | None = None
    # Events associated with the domain
    events: list[Event] = Field(default_factory=list)
    # Links related to the domain
    links: list[Link] = Field(default_factory=list)
    # Entities associated with the domain
    entities: list[Entity] = Field(default_factory=list)
    # WHOIS server for the domain
    port43: str = Field(default_factory=str)
    # Network information for the domain
    network: IPNetwork | None = None
    # Type of the object (always "domain" for Domain)
    objectClassName: str | None = None

    secureDNS: SecureDNS | None = None

    nameservers: list[Nameserver] = Field(default_factory=list)


class AutNum(BaseModel):
    """Represents an Autonomous System Number in the RDAP response."""

    # list of conformance levels
    rdapConformance: list[str] = Field(default_factory=list)
    # Notices related to the AS number
    notices: list[Notice] = Field(default_factory=list)
    # A unique identifier for the AS number
    handle: str | None = None
    # The starting AS number in the range
    startAutnum: int | None = None
    # The ending AS number in the range (same as startAutnum for single AS)
    endAutnum: int | None = None
    # Name of the AS
    name: str | None = None
    # WHOIS server for the AS number
    port43: str | None = None

    # Type of the object (always "autnum" for AutNum)
    objectClassName: str | None = None

    # Events associated with the AS number
    events: list[Event] = Field(default_factory=list)
    # Links related to the AS number
    links: list[Link] = Field(default_factory=list)
    # Entities associated with the AS number
    entities: list[Entity] = Field(default_factory=list)
    # Status of the AS number
    status: list[str] = Field(default_factory=list)

    # Remarks about the AS number
    remarks: list[Remark] = Field(default_factory=list)


Entity.model_rebuild()
