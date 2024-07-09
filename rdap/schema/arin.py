from pydantic import BaseModel, Field
from datetime import datetime
from typing import Any

class Link(BaseModel):
    """Represents a hyperlink in the RDAP response."""
    # The label or description of the link
    value: str
    # The relationship of the link to the current object
    rel: str
    # The MIME type of the target resource
    type: str
    # The URL of the link
    href: str

class Event(BaseModel):
    """Represents a timestamped event in the lifecycle of an RDAP object."""
    # The type of event (e.g., "registration", "last changed")
    eventAction: str
    # The date and time of the event
    eventDate: datetime

class Notice(BaseModel):
    """Represents a notice or message in the RDAP response."""
    # The title of the notice
    title: str
    # A list of text lines comprising the notice
    description: list[str]
    # Optional links related to the notice
    links: list[Link] | None = None

class VCardValue(BaseModel):
    """Represents additional properties for vCard values."""
    # Types associated with the vCard value (e.g., "work", "voice" for telephone)
    type: list[str] | None = None

class VCardEntry(BaseModel):
    """Represents a single entry in a vCard."""
    # The name of the vCard property (e.g., "version", "fn", "adr")
    name: str
    # Metadata associated with the entry
    meta: dict = Field(default_factory=dict)
    # The value of the vCard property
    value: str | list[str] | VCardValue

class VCard(BaseModel):
    """Represents a vCard (contact information) in the RDAP response."""
    version: VCardEntry
    # Formatted Name
    fn: VCardEntry
    # Address
    adr: VCardEntry | None = None
    # Kind of object (e.g., individual, org, group)
    kind: VCardEntry | None = None
    email: VCardEntry | None = None
    # Telephone
    tel: VCardEntry | None = None
    # Name components
    n: VCardEntry | None = None
    # Organization
    org: VCardEntry | None = None

class Remark(BaseModel):
    """Represents a remark or comment in the RDAP response."""
    # The title of the remark
    title: str
    # A list of text lines comprising the remark
    description: list[str]

class Entity(BaseModel):
    """Represents an entity (organization, individual, or role) in the RDAP response."""
    # A unique identifier for the entity
    handle: str
    # Contact information in vCard format
    vcardArray: list[str | list[VCardEntry] | list[Any]] = Field(default_factory=list)
    # Roles of the entity (e.g., registrant, technical, administrative)
    roles: list[str]
    # Links related to the entity
    links: list[Link]
    # Events associated with the entity
    events: list[Event]
    # Status of the entity
    status: list[str] | None = None
    # WHOIS server for the entity
    port43: str
    # Type of the object (always "entity" for Entity)
    objectClassName: str
    # Additional remarks about the entity
    remarks: list[Remark] | None = None
    # Nested entities (e.g., contacts within an organization)
    entities: list['Entity'] | None = None


class IPNetwork(BaseModel):
    """Represents an IP network in the RDAP response."""
    # list of conformance levels
    rdapConformance: list[str] = Field(default_factory=list)
    # Notices related to the IP network
    notices: list[Notice] = Field(default_factory=list)
    # A unique identifier for the IP network
    handle: str
    # The first IP address in the network range
    startAddress: str
    # The last IP address in the network range
    endAddress: str
    # IP version (v4 or v6)
    ipVersion: str
    # Name of the network
    name: str
    # Type of the network allocation
    type: str
    # Handle of the parent network
    parentHandle: str
    # Additional remarks about the network
    remarks: list[Remark] | None = None
    # Events associated with the network
    events: list[Event]
    # Links related to the network
    links: list[Link]
    # Entities associated with the network
    entities: list[Entity]
    # WHOIS server for the network
    port43: str
    # Status of the network
    status: list[str]
    # Type of the object (always "ip network" for IPNetwork)
    objectClassName: str
    # CIDR notation for the network
    cidr0_cidrs: list[dict]
    # Origin AS numbers for the network
    arin_originas0_originautnums: list

class Domain(BaseModel):
    """Represents a domain name in the RDAP response."""
    # list of conformance levels
    rdapConformance: list[str] = Field(default_factory=list)
    # Notices related to the domain
    notices: list[Notice] = Field(default_factory=list)
    # A unique identifier for the domain
    handle: str
    # The domain name in LDH (Letter Digit Hyphen) format
    ldhName: str
    # Events associated with the domain
    events: list[Event]
    # Links related to the domain
    links: list[Link]
    # Entities associated with the domain
    entities: list[Entity]
    # WHOIS server for the domain
    port43: str
    # Network information for the domain
    network: IPNetwork
    # Type of the object (always "domain" for Domain)
    objectClassName: str

class AutNum(BaseModel):
    """Represents an Autonomous System Number in the RDAP response."""
    # list of conformance levels
    rdapConformance: list[str] = Field(default_factory=list)
    # Notices related to the AS number
    notices: list[Notice] = Field(default_factory=list)
    # A unique identifier for the AS number
    handle: str
    # The starting AS number in the range
    startAutnum: int
    # The ending AS number in the range (same as startAutnum for single AS)
    endAutnum: int
    # Name of the AS
    name: str
    # WHOIS server for the AS number
    port43: str

    # Type of the object (always "autnum" for AutNum)
    objectClassName: str

    # Events associated with the AS number
    events: list[Event] = Field(default_factory=list)
    # Links related to the AS number
    links: list[Link] = Field(default_factory=list)
    # Entities associated with the AS number
    entities: list[Entity] = Field(default_factory=list)
    # Status of the AS number
    status: list[str] = Field(default_factory=list)

Entity.update_forward_refs()