from contextvars import ContextVar
import pydantic
from datetime import datetime
from rdap.exceptions import RdapHTTPError

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

    entities: dict = pydantic.Field(default_factory=dict)

    def update_source(self, handle:str, created:datetime | None, updated:datetime | None):
        self.sources[-1].handle = handle
        self.sources[-1].created = created
        self.sources[-1].updated = updated

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

    def get(self, typ:str, handle:str):
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


