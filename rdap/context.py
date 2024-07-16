from contextvars import ContextVar
import pydantic
from datetime import datetime

from rdap.schema.rdap import Entity, AutNum, IPNetwork, Domain

__all__ = [
    "rdap_request",
    "RdapRequestContext",
    "RdapRequestState",
]

class RdapSource(pydantic.BaseModel):
    urls: list[str] = pydantic.Field(default_factory=list)
    handle: str | None = None
    created: datetime | None = None
    updated: datetime | None = None

class RdapRequestState(pydantic.BaseModel):
    sources: list[RdapSource] = pydantic.Field(default_factory=list)
    client: object | None = None #RdapClient

    def update_source(self, entity:Entity | AutNum | IPNetwork | Domain):
        self.sources[-1].handle = entity.handle
        self.sources[-1].created = entity.events[-1].eventDate
        self.sources[-1].updated = entity.events[0].eventDate

# context that holds the currently requested rdap url

rdap_request = ContextVar("rdap_request", default=RdapRequestState())

# context manager to set the rdap url
# can be nested

class RdapRequestContext:

    def __init__(self, url:str = None, client:object = None):
        self.url = url
        self.token = None
        self.client = client

    def __enter__(self):
        
        # get existing state

        state = rdap_request.get()

        if state and self.url:
            state.sources.append(RdapSource(urls=[self.url]))
        else:
            state = RdapRequestState(sources=[RdapSource(urls=[self.url] if self.url else [])])
            self.token = rdap_request.set(state)

        if self.client:
            state.client = self.client

        return self

    def __exit__(self, *exc):
        if self.token:
            rdap_request.reset(self.token)

    def push_url(self, url:str):
        state = rdap_request.get()
        state.sources[-1].urls.append(url)