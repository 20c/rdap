"""
Rdap data parsers for ARIN data
"""

import ipaddress
from rdap.exceptions import RdapHTTPError

from rdap.schema.normalized import (
    Contact,
    Nameserver,
    DNSSEC
)

from rdap.context import rdap_request, RdapRequestState, RdapRequestContext

import rdap.schema.rdap as schema

__all__ = [
    "org_name_from_entity",
    "org_name",
    "contacts_from_entity",
    "contacts",
    "address_from_entity",
    "address",
    "prefix",
    "parent_prefix",
    "secure_dns",
    "nameservers",
]

def address_from_entity(entity: schema.Entity) -> str | None:
    """
    Will parse an address from an entity

    Will return the address if it can be found, otherwise None
    """
    # address will be through entities
    # looking for vcardArray with ["adr", {"label": address}, "text"] to
    # establish the address entry

    for vcard in entity.vcardArray[1:]:
        for vcard_entry in vcard:
            if vcard_entry[0] == "adr":
                return vcard_entry[1].get("label")

    return None

def address(entity: schema.AutNum | schema.IPNetwork | schema.Domain) -> str | None:
    """
    Will parse an address from an object

    Will return the address if it can be found, if no address
    can be found, will return None
    """

    for _entity in entity.entities:
        address = address_from_entity(_entity)
        if address:
            return address

    return None

def contacts_from_entity(entity: schema.Entity, deep:bool = True) -> list[Contact]:

    """
    Will parse contacts from an entity

    Will return a list of contacts if it can be found, otherwise an empty list

    vcard entriews that are considered:

    ["email", {}, "text", email]
    ["tel", {}, "text", phone]
    ["fn", {}, "text", name]

    A contact is considered if `fn` and either of `email` or `tel` is present

    If deep is set to True, will also check nessted entities.
    """

    contacts = []

    for vcard in entity.vcardArray[1:]:

        contact = Contact(
            name = "",
            roles = getattr(entity, "roles", []) or []
        )
        for vcard_entry in vcard:
            if vcard_entry[0] == "fn":
                contact.name = vcard_entry[3]
            if vcard_entry[0] == "email":
                contact.email = vcard_entry[3]
            if vcard_entry[0] == "tel":
                contact.phone = vcard_entry[3]

            if contact.name and (contact.email or contact.phone):
                contacts.append(contact)

        if deep and getattr(entity, "entities", None):
            for _entity in entity.entities:
                contacts.extend(contacts_from_entity(_entity, deep=True))

    # remove dupes
    contacts = list(set(contacts))

    recurse_contacts(entity, contacts, entity.roles)

    return contacts

def contacts(entity: schema.AutNum | schema.IPNetwork | schema.Domain, deep:bool = True) -> list[Contact]:

    """
    Will parse contacts from an object

    Will return a list of contacts if it can be found, otherwise an empty list

    If deep is set to True, will also check nessted entities.
    """

    contacts = []

    for _entity in entity.entities:
        contacts.extend(contacts_from_entity(_entity, deep=deep))

    # remove dupes
    contacts = list(set(contacts))

    # now cycle through and combine contacts
    #
    # check `name`, `phone` and `email` and if all three
    # are the same, combine the roles

    combined_contacts = {}

    for _contact in contacts:
        key = f"{_contact.name}-{_contact.email}-{_contact.phone}"

        if key in combined_contacts:
            combined_contacts[key].roles.extend(_contact.roles)
        else:
            combined_contacts[key] = _contact

    contacts = list(combined_contacts.values())

    return contacts

def recurse_contacts(entity: schema.Entity, contacts: list[Contact], roles: list[str]) -> list[Contact]:
    
    request_state: RdapRequestState = rdap_request.get()
    client = request_state.client

    # if role is in settings to recurse, try to do a lookup
    if entity.handle and client:

        handle_url = entity.self_link
        if not handle_url:
            handle_url = client.get_entity_url(entity.handle)

        if not client.recurse_roles.isdisjoint(roles):
            try:
                with RdapRequestContext(url=handle_url, client=client):
                    r_entity = client.get_entity(entity.handle)
                    r_entity = r_entity.normalized
                    contacts.extend([
                        Contact(**contact) for contact in r_entity["contacts"]
                    ])
            # check for HTTP Errors to ignore
            except RdapHTTPError:
                # TODO: Do we ever want to raise on broken links?
                # Probably not.
                pass


def org_name_from_entity(entity: schema.Entity) -> str | None:
    """
    Will parse an org name from an entity

    Will return the org name if it can be found, otherwise None
    """
    # org name will be through entities
    # looking for vcardArray with ["kind", {}, "text", org] to
    # establish the org entry
    #
    # in the same vcardArray, looking for ["fn", {}, "text", name]

    kind_is_org = False
    org_name = None

    for vcard in entity.vcardArray:
        if vcard[0] == "kind" and vcard[3] == "org":
            kind_is_org = True
        if vcard[0] == "fn":
            org_name = vcard[3]
    
    if kind_is_org and org_name:
        return org_name

    return None

def org_name(entity: schema.AutNum | schema.IPNetwork | schema.Domain) -> str | None:
    """
    Will parse an org name from an object

    Will return the org name if it can be found, if no org name
    can be found, will return entity name or None
    """

    for _entity in entity.entities:
        name = org_name_from_entity(_entity)
        if name:
            return name

    return entity.name or None


def prefix(ip_network: schema.IPNetwork) -> ipaddress.IPv4Network | ipaddress.IPv6Network:
    """
    Will return the CIDR of an IPNetwork object
    "cidr0_cidrs" : [ {
        "v4prefix" : "206.41.110.0",
        "length" : 24
    } ],
    """

    cidr = ip_network.cidr0_cidrs[0]

    if "v4prefix" in cidr:
        return ipaddress.IPv4Network(f"{cidr['v4prefix']}/{cidr['length']}")
    
    if "v6prefix" in cidr:
        return ipaddress.IPv6Network(f"{cidr['v6prefix']}/{cidr['length']}")

    return None

def parent_prefix(ip_network: schema.IPNetwork) -> ipaddress.IPv4Network | ipaddress.IPv6Network | None:
    """
    Parent network prefix from `parentHandle`

    "parentHandle" : "NET-206-0-0-0-0",
    """

    if not ip_network.parentHandle:
        return None

    # Extract the IP address part from the parentHandle
    ip_parts = ip_network.parentHandle.split('-')[1:-1]
    
    # Reconstruct the IP address string
    ip_str = '.'.join(ip_parts)
    
    # Determine the appropriate prefix length based on the number of non-zero octets
    non_zero_octets = sum(1 for part in ip_parts if part != '0')
    prefix_length = non_zero_octets * 8
    
    # Construct the CIDR notation
    cidr = f"{ip_str}/{prefix_length}"
    
    try:
        # Attempt to create an IP network object
        return ipaddress.ip_network(cidr, strict=False)
    except ValueError:
        # If the IP address is invalid, return None
        return None


def secure_dns(domain: schema.Domain) -> DNSSEC:
    """
    Will determine if the domain has secure DNS

    This is determined by the `secureDNS` object

    If `delegationSigned` or `zeroSigned` is True, will return secure

    If both are False, will return insecure

    If secureDNS is not present, or both are None, will return unknown
    """

    if not domain.secureDNS:
        return DNSSEC.unknown

    if domain.secureDNS.delegationSigned is None and domain.secureDNS.zeroSigned is None:
        return DNSSEC.unknown

    if domain.secureDNS.delegationSigned or domain.secureDNS.zeroSigned:
        return DNSSEC.secure

    return DNSSEC.insecure


def nameservers(domain: schema.Domain) -> list[Nameserver]:
    """
    Returns normalized nameservers from a domain object
    """

    nameservers = []

    for nameserver in domain.nameservers:
        nameservers.append(Nameserver(host=nameserver.ldhName))

    return nameservers