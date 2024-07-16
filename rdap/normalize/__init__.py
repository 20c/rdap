"""
Contains a set of functions to parse various rdap data properties
"""

import json

import rdap.normalize.base as base
import rdap.normalize.geo as geo

import rdap.schema.normalized as schema 
from rdap.schema.source import (
    autnum_model,
    entity_model,
    ip_network_model,
    domain_model,
)

from rdap.context import rdap_request, RdapRequestState


__all__ = [
    "normalize",
]

HANDLERS = {
    "arin": base,
    "ripe": base,
    "apnic": base,
    "afrinic": base,
    "lacnic": base,
    # domains are weird.
    None: base
}

def get_sources(
    state: RdapRequestState, 
    handle: str,
    entity: schema.Network | schema.IPNetwork | schema.Domain | schema.Entity
) -> list[schema.Source]:

    sources = []
    
    for source in state.sources:

        if not source.urls or not source.handle:
            continue

        source = schema.Source(
            handle = source.handle,
            created = source.created,
            updated = source.updated,
            urls = source.urls,
        )

        sources.append(source)


    return sources


def normalize(data: dict, rir: str, typ: str) -> dict:
    """
    Normalize data based on RIR

    Will return a normalized dict based on the RIR
    """
    
    if typ == "autnum":
        return normalize_autnum(data, rir)
    elif typ == "entity":
        return normalize_entity(data, rir)
    elif typ == "ip":
        return normalize_ip(data, rir)
    elif typ == "domain":
        return normalize_domain(data, rir)
    else:
        raise ValueError(f"Type {typ} not supported")

def normalize_autnum(data: dict, rir: str) -> dict:
    """
    Normalize data based on RIR: Autnum

    Will return a normalized dict based on the RIR
    """
    handler = HANDLERS.get(rir)
    if not handler:
        raise ValueError(f"RIR {rir} not supported")

    current_rdap_request = rdap_request.get()

    rdap_autnum = autnum_model(rir)(**data)

    current_rdap_request.update_source(rdap_autnum)

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

    return json.loads(net.model_dump_json())

def normalize_ip(data: dict, rir: str) -> dict:
    """
    Normalize data based on RIR: IPNetwork

    Will return a normalized dict based on the RIR
    """
    handler = HANDLERS.get(rir)
    if not handler:
        raise ValueError(f"RIR {rir} not supported")

    current_rdap_request = rdap_request.get()

    rdap_ip_network = ip_network_model(rir)(**data)

    current_rdap_request.update_source(rdap_ip_network)

    prefix = handler.prefix(rdap_ip_network)

    net = schema.IPNetwork(
        created = rdap_ip_network.events[-1].eventDate,
        updated = rdap_ip_network.events[0].eventDate,
        name = rdap_ip_network.name,
        prefix = prefix,
        parent=  handler.parent_prefix(rdap_ip_network),
        version = prefix.version, 
        type = rdap_ip_network.type,
        # TODO: What happens if more than one status is in there?
        status = rdap_ip_network.status[0] if rdap_ip_network.status else None,
        contacts = handler.contacts(rdap_ip_network),
    )

    if current_rdap_request:
        net.sources = get_sources(current_rdap_request, rdap_ip_network.handle, net)

    return json.loads(net.model_dump_json())

def normalize_domain(data: dict, rir: str) -> dict:
    """
    Normalize data based on RIR: Domain

    Will return a normalized dict based on the RIR
    """
    handler = HANDLERS.get(rir)
    if not handler:
        raise ValueError(f"RIR {rir} not supported")

    current_rdap_request = rdap_request.get()

    rdap_domain = domain_model(rir)(**data)

    current_rdap_request.update_source(rdap_domain)

    net = schema.Domain(
        created = rdap_domain.events[-1].eventDate,
        updated = rdap_domain.events[0].eventDate,
        name = rdap_domain.ldhName,
        handle = rdap_domain.handle,
        dns_sec = handler.secure_dns(rdap_domain),
        contacts = handler.contacts(rdap_domain),
        nameservers = handler.nameservers(rdap_domain),
    )

    if current_rdap_request:
        net.sources = get_sources(current_rdap_request, rdap_domain.handle, net)

    return json.loads(net.model_dump_json())


def normalize_entity(data: dict, rir: str) -> dict:
    """
    Normalize data based on RIR: Entity

    Will return a normalized dict based on the RIR
    """
    handler = HANDLERS.get(rir)
    if not handler:
        raise ValueError(f"RIR {rir} not supported")

    current_rdap_request = rdap_request.get()

    rdap_entity = entity_model(rir)(**data)

    current_rdap_request.update_source(rdap_entity)

    org_name = handler.org_name_from_entity(rdap_entity)

    if org_name:
        org = schema.Organization(name=org_name)
    else:
        org = None

    address = handler.address_from_entity(rdap_entity)

    entity = schema.Entity(
        created = rdap_entity.events[-1].eventDate,
        updated = rdap_entity.events[0].eventDate,
        name = rdap_entity.handle,
        organization = org,
        contacts = handler.contacts_from_entity(rdap_entity),
    )

    location = geo.normalize(address, entity.updated) 
    if location:
        entity.location = location

    if current_rdap_request:
        entity.sources = get_sources(current_rdap_request, rdap_entity.handle, entity)

    return json.loads(entity.model_dump_json())