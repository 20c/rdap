# API

## Retrieve objects

```python
import rdap

# instantiate client
client = rdap.RdapClient()

# asn
as63311 = client.get_asn(63311)

# domain
domain = client.get_domain('example.com')

# ip
ip = client.get_ip('206.41.110.0')

# entity
entity = client.get_entity('NETWO7047-ARIN')
```

## Output normalized data (ASN example)

```python
import json
import rdap

# instantiate client
client = rdap.RdapClient()

# request asn
as63311 = client.get_asn(63311)

# normalized dict
print(json.dumps(as63311.normalized, indent=2))
```

Output:
```json
{
  "created": "2014-11-17T14:28:43-05:00",
  "updated": "2018-10-24T22:58:16-04:00",
  "asn": 63311,
  "name": "20C",
  "organization": {
    "name": "20C, LLC"
  },
  "locations": [
    {
      "updated": "2014-08-05T15:21:11-04:00",
      "country": null,
      "city": null,
      "postal_code": null,
      "address": "303 W Ohio #1701\nChicago\nIL\n60654\nUnited States",
      "geo": null,
      "floor": null,
      "suite": null
    },
    {
      "updated": "2023-08-02T14:15:09-04:00",
      "country": null,
      "city": null,
      "postal_code": null,
      "address": "603 Discovery Dr\nWest Chicago\nIL\n60185\nUnited States",
      "geo": null,
      "floor": null,
      "suite": null
    }
  ],
  "contacts": [
    {
      "created": "2014-07-03T23:22:49-04:00",
      "updated": "2023-08-02T14:15:09-04:00",
      "name": "Network Engineers",
      "roles": [
        "abuse",
        "admin",
        "technical"
      ],
      "phone": "+1 978-636-0020",
      "email": "neteng@20c.com"
    }
  ],
  "sources": [
    {
      "created": "2014-11-17T14:28:43-05:00",
      "updated": "2018-10-24T22:58:16-04:00",
      "handle": "AS63311",
      "urls": [
        "https://rdap.org/autnum/63311",
        "https://rdap.arin.net/registry/autnum/63311"
      ],
      "description": null
    }
  ]
}
```

## Work with normalized data through pydantic models

```python
import rdap

from rdap.schema.normalized import Network

# instantiate client
client = rdap.RdapClient()

# request asn
as63311 = Network(**client.get_asn(63311).normalized)

for contact in as63311.contacts:
    print(contact.name, contact.email)
```