"""
Rdap data parsers for ARIN data
"""

import rdap.schema.arin as schema

__all__ = [
    "org_name_from_entity",
    "org_name"
]

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