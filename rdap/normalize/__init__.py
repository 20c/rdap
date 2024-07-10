"""
Contains a set of functions to parse various rdap data properties
"""

import rdap.normalize.arin as arin

import rdap.schema.normalized as schema 
from rdap.schema.source import autnum_model

__all__ = [
    "normalize",
]

HANDLERS = {
    "arin": arin
}

def normalize(data: dict, rir: str, typ: str) -> dict:
    """
    Normalize data based on RIR

    Will return a normalized dict based on the RIR
    """
    handler = HANDLERS.get(rir)
    
    if not handler:
        raise ValueError(f"RIR {rir} not supported")

    if typ == "autnum":
        model = autnum_model(rir)(**data)
        org_name = handler.org_name(model)
        print("org_name: ", org_name)

    return data