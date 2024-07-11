"""
Rdap data parsers for ARIN data
"""

from rdap.schema.normalized import (
    Contact,
)

import rdap.schema.arin as schema

__all__ = [
    "org_name_from_entity",
    "org_name"
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
            roles = getattr(entity, "roles", [])
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

    return contacts

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