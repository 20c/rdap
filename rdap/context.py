from contextvars import ContextVar
import pydantic
from datetime import datetime

__all__ = [
    "rdap_request",
    "RdapRequestContext",
    "RdapRequestState",
]

class RdapRequestState(pydantic.BaseModel):
    urls: list[str] = pydantic.Field(default_factory=list)

# context that holds the currently requested rdap url

rdap_request = ContextVar("rdap_request", default=RdapRequestState())

# context manager to set the rdap url
# can be nested

class RdapRequestContext:

    def __init__(self, url:str = None):
        self.url = url
        self.token = None

    def __enter__(self):
        
        # get existing state

        state = rdap_request.get()

        if state and self.url:
            state.urls.append(self.url)
        else:
            state = RdapRequestState(urls=[self.url] if self.url else [])
            self.token = rdap_request.set(state)



    def __exit__(self, *exc):
        if self.token:
            rdap_request.reset(self.token)