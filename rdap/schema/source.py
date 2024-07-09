import rdap.schema.arin as arin

__all__ = [
    "SCHEMAS_BY_RIR",
    "ip_network_model",
    "domain_model",
    "autnum_model",
    "entity_model",
]

SCHEMAS_BY_RIR = {
    "arin": arin,
}

def ip_network_model(rir:str):
    return SCHEMAS_BY_RIR[rir].IPNetwork

def domain_model(rir:str):
    return SCHEMAS_BY_RIR[rir].Domain

def autnum_model(rir:str):
    return SCHEMAS_BY_RIR[rir].AutNum

def entity_model(rir:str):
    return SCHEMAS_BY_RIR[rir].Entity
