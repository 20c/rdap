"""Contact management for RDAP requests."""

from contextvars import ContextVar
from datetime import datetime
from typing import List, Optional

import pydantic

from rdap.exceptions import RdapHTTPError

__all__ = [
    "rdap_request",
    "RdapRequestContext",
    "RdapRequestState",
]


class RdapSource(pydantic.BaseModel):
    """Describes a source of RDAP data."""

    # urls requested for this source
    urls: List[str] = pydantic.Field(default_factory=list)

    # rdap object handle
    handle: Optional[str] = None

    # source creation date (if available)
    created: Optional[datetime] = None

    # source last update date (if available)
    updated: Optional[datetime] = None


class RdapRequestState(pydantic.BaseModel):
    """Describe the current rdap request, tracking sources queried
    and entities retrieved.
    """

    # list of sources for the current request
    sources: List[RdapSource] = pydantic.Field(default_factory=list)

    # reference to the rdap client instance
    client: Optional[object] = None

    # cache of entities (to avoid duplicate requests to the same entity
    # within the current request context)
    entities: dict = pydantic.Field(default_factory=dict)

    def update_source(
        self,
        handle: str,
        created: Optional[datetime],
        updated: Optional[datetime],
    ):
        """Update the current source with the handle and dates."""
        self.sources[-1].handle = handle
        self.sources[-1].created = created
        self.sources[-1].updated = updated


# context that holds the currently requested rdap url

rdap_request = ContextVar("rdap_request", default=RdapRequestState())

# context manager to set the rdap url
# can be nested


class RdapRequestContext:
    """Opens a request context

    If no state is present, a new state is created.

    If a state is present, a new source is added to the state.
    """

    def __init__(self, url: str = None, client: object = None):
        self.url = url
        self.token = None
        self.client = client

    def __enter__(self):
        # get existing state

        state = rdap_request.get()

        if state and self.url:
            state.sources.append(RdapSource(urls=[self.url]))
        else:
            state = RdapRequestState(
                sources=[RdapSource(urls=[self.url] if self.url else [])],
            )
            self.token = rdap_request.set(state)

        if self.client:
            state.client = self.client

        return self

    def __exit__(self, *exc):
        if self.token:
            rdap_request.reset(self.token)

    def push_url(self, url: str):
        state = rdap_request.get()
        state.sources[-1].urls.append(url)

    def get(self, typ: str, handle: str):
        state = rdap_request.get()
        client = state.client

        if typ not in ["entity", "ip", "domain", "autnum"]:
            raise ValueError(f"Invalid type: {typ}")

        if state.entities.get(handle):
            return state.entities[handle]
        try:
            get = getattr(client, f"get_{typ}")
            r_entity = get(handle).normalized
            state.entities[handle] = r_entity
            return r_entity
        except RdapHTTPError:
            state.entities[handle] = {}
            return {}
