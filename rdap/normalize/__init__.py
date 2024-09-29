"""Contains a set of functions to parse various rdap data properties"""

import json
from typing import List, Union

import rdap.schema.normalized as schema
from rdap.context import RdapRequestState, rdap_request
from rdap.normalize import afrinic, apnic, arin, base, lacnic, ripe
from rdap.schema.source import (
    autnum_model,
    domain_model,
    entity_model,
    ip_network_model,
)

__all__ = [
    "normalize",
    "normalize_autnum",
    "normalize_entity",
    "normalize_ip",
    "normalize_domain",
    "get_sources",
]

HANDLERS = {
    "arin": arin.Handler(),
    "ripe": ripe.Handler(),
    "apnic": apnic.Handler(),
    "afrinic": afrinic.Handler(),
    "lacnic": lacnic.Handler(),
    # other (verisign for domains etc.)
    None: base.Handler(),
}


def get_sources(
    state: RdapRequestState,
    handle: str,
    entity: Union[schema.Network, schema.IPNetwork, schema.Domain, schema.Entity],
) -> List[schema.Source]:
    sources = []

    for source in state.sources:
        if not source.urls or not source.handle:
            continue

        source = schema.Source(
            handle=source.handle,
            created=source.created,
            updated=source.updated,
            urls=source.urls,
        )

        sources.append(source)

    return sources


def normalize(data: dict, rir: str, typ: str) -> dict:
    """Normalize data based on RIR

    Will return a normalized dict based on the RIR
    """
    if typ == "autnum":
        return normalize_autnum(data, rir)
    if typ == "entity":
        return normalize_entity(data, rir)
    if typ == "ip":
        return normalize_ip(data, rir)
    if typ == "domain":
        return normalize_domain(data, rir)
    raise ValueError(f"Type {typ} not supported")


def normalize_autnum(data: dict, rir: str) -> dict:
    """Normalize data based on RIR: Autnum

    Will return a normalized dict based on the RIR
    """
    handler = HANDLERS.get(rir)
    if not handler:
        raise ValueError(f"RIR {rir} not supported")

    current_rdap_request = rdap_request.get()

    rdap_autnum = autnum_model(rir)(**data)

    current_rdap_request.update_source(
        rdap_autnum.handle,
        **handler.dates(rdap_autnum.events),
    )

    org_name = handler.org_name(rdap_autnum)
    org = schema.Organization(name=org_name)

    net = schema.Network(
        name=rdap_autnum.name,
        organization=org,
        asn=rdap_autnum.startAutnum,
        contacts=handler.contacts(rdap_autnum),
        locations=handler.locations(rdap_autnum),
        **handler.dates(rdap_autnum.events),
    )

    if current_rdap_request:
        net.sources = get_sources(current_rdap_request, rdap_autnum.handle, net)

    return json.loads(net.model_dump_json())


def normalize_ip(data: dict, rir: str) -> dict:
    """Normalize data based on RIR: IPNetwork

    Will return a normalized dict based on the RIR
    """
    handler = HANDLERS.get(rir)
    if not handler:
        raise ValueError(f"RIR {rir} not supported")

    current_rdap_request = rdap_request.get()

    rdap_ip_network = ip_network_model(rir)(**data)

    current_rdap_request.update_source(
        rdap_ip_network.handle,
        **handler.dates(rdap_ip_network.events),
    )

    prefix = handler.prefix(rdap_ip_network)

    net = schema.IPNetwork(
        name=rdap_ip_network.name,
        prefix=prefix,
        parent=handler.parent_prefix(rdap_ip_network),
        version=handler.ip_version(rdap_ip_network),
        type=rdap_ip_network.type,
        # TODO: What happens if more than one status is in there?
        status=rdap_ip_network.status[0] if rdap_ip_network.status else None,
        contacts=handler.contacts(rdap_ip_network),
        **handler.dates(rdap_ip_network.events),
    )

    if current_rdap_request:
        net.sources = get_sources(current_rdap_request, rdap_ip_network.handle, net)

    return json.loads(net.model_dump_json())


def normalize_domain(data: dict, rir: str) -> dict:
    """Normalize data based on RIR: Domain

    Will return a normalized dict based on the RIR
    """
    handler = HANDLERS.get(rir)
    if not handler:
        raise ValueError(f"RIR {rir} not supported")

    current_rdap_request = rdap_request.get()

    rdap_domain = domain_model(rir)(**data)

    current_rdap_request.update_source(
        rdap_domain.handle,
        **handler.dates(rdap_domain.events),
    )

    net = schema.Domain(
        name=rdap_domain.ldhName,
        handle=rdap_domain.handle,
        dns_sec=handler.secure_dns(rdap_domain),
        contacts=handler.contacts(rdap_domain),
        nameservers=handler.nameservers(rdap_domain),
        **handler.dates(rdap_domain.events),
    )

    if current_rdap_request:
        net.sources = get_sources(current_rdap_request, rdap_domain.handle, net)

    return json.loads(net.model_dump_json())


def normalize_entity(data: dict, rir: str) -> dict:
    """Normalize data based on RIR: Entity

    Will return a normalized dict based on the RIR
    """
    handler = HANDLERS.get(rir)
    if not handler:
        raise ValueError(f"RIR {rir} not supported")

    current_rdap_request = rdap_request.get()

    rdap_entity = entity_model(rir)(**data)

    current_rdap_request.update_source(
        rdap_entity.handle,
        **handler.dates(rdap_entity.events),
    )

    org_name = handler.org_name_from_entity(rdap_entity)

    if org_name:
        org = schema.Organization(name=org_name)
    else:
        org = None

    entity = schema.Entity(
        name=rdap_entity.handle,
        organization=org,
        contacts=handler.contacts_from_entity(rdap_entity),
        locations=handler.locations_from_entity(rdap_entity),
        **handler.dates(rdap_entity.events),
    )

    if current_rdap_request:
        entity.sources = get_sources(current_rdap_request, rdap_entity.handle, entity)

    return json.loads(entity.model_dump_json())
