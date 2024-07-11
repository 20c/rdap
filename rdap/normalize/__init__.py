"""
Contains a set of functions to parse various rdap data properties
"""

import rdap.normalize.arin as arin
import rdap.normalize.geo as geo

import rdap.schema.normalized as schema 
from rdap.schema.source import autnum_model
from rdap.context import rdap_request, RdapRequestState


__all__ = [
    "normalize",
]

HANDLERS = {
    "arin": arin
}

def get_sources(
    state: RdapRequestState, 
    handle: str,
    entity: schema.Network | schema.IPNetwork | schema.Domain | schema.Entity
) -> list[schema.Source]:

    sources = []

    print(state.model_dump())

    sources.append(schema.Source(
        created = entity.created,
        updated = entity.updated,
        handle = handle,
        urls = state.urls
    ))

    return sources


def normalize(data: dict, rir: str, typ: str) -> dict:
    """
    Normalize data based on RIR

    Will return a normalized dict based on the RIR
    """
    handler = HANDLERS.get(rir)
    
    if not handler:
        raise ValueError(f"RIR {rir} not supported")

    current_rdap_request = rdap_request.get()

    if typ == "autnum":
        rdap_autnum = autnum_model(rir)(**data)
        org_name = handler.org_name(rdap_autnum)
        org = schema.Organization(name=org_name)
        address = handler.address(rdap_autnum)


        net = schema.Network(
            created = rdap_autnum.events[-1].eventDate,
            updated = rdap_autnum.events[0].eventDate,
            name = rdap_autnum.name,
            organization = org,
            asn = rdap_autnum.startAutnum,
            contacts = handler.contacts(rdap_autnum),
        )

        location = geo.normalize(address, net.updated) 
        if location:
            net.location = location

        if current_rdap_request:
            net.sources = get_sources(current_rdap_request, rdap_autnum.handle, net)

        print(net.model_dump_json(indent=2))


    return data