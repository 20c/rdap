"""Some case specific normalization functions for RIPE data.
"""

import rdap.schema.rdap as schema
from rdap.normalize import base
from typing import Union

__all__ = [
    "Handler",
]


class Handler(base.Handler):
    """RIPE sometimes puts org name into the remarks
    """

    def org_name(
        self, entity: Union[schema.AutNum, schema.IPNetwork, schema.Domain],
    ) -> Union[str, None]:
        """If super() return None or equal to entity.name try checking
        remarks for an entry where title == "description"
        """
        org_name = super().org_name(entity)

        if org_name is None or org_name == entity.name:
            for remark in entity.remarks:
                if remark.title == "description":
                    org_name = remark.description[0]
                    break

        return org_name
