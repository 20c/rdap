from rdap.schema import rdap

__all__ = [
    "SCHEMAS_BY_RIR",
    "ip_network_model",
    "domain_model",
    "autnum_model",
    "entity_model",
]

SCHEMAS_BY_RIR = {
    "arin": rdap,
    "ripe": rdap,
    "apnic": rdap,
    "afrinic": rdap,
    "lacnic": rdap,
    None: rdap,
}


def ip_network_model(rir: str) -> rdap.IPNetwork:
    """Returns pydantic model for IPNetwork for the given RIR

    Arguments:
    - rir: str: RIR name (e.g., "arin", "ripe", "apnic", "afrinic", "lacnic")

    """
    return SCHEMAS_BY_RIR[rir].IPNetwork


def domain_model(rir: str) -> rdap.Domain:
    """Returns pydantic model for Domain for the given RIR

    Arguments:
    - rir: str: RIR name (e.g., "arin", "ripe", "apnic", "afrinic", "lacnic")

    """
    return SCHEMAS_BY_RIR[rir].Domain


def autnum_model(rir: str) -> rdap.AutNum:
    """Returns pydantic model for AutNum for the given RIR

    Arguments:
    - rir: str: RIR name (e.g., "arin", "ripe", "apnic", "afrinic", "lacnic")

    """
    return SCHEMAS_BY_RIR[rir].AutNum


def entity_model(rir: str) -> rdap.Entity:
    """Returns pydantic model for Entity for the given RIR

    Arguments:
    - rir: str: RIR name (e.g., "arin", "ripe", "apnic", "afrinic", "lacnic")

    """
    return SCHEMAS_BY_RIR[rir].Entity
