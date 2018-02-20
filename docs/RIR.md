
### ARIN: https://rdap.arin.net/

- org data in nested vcard under `roles`: "registrant"
- has email addresses on entities


### RIPE: https://rdap.db.ripe.net/

- no org handle on rdap autnums
  * emailed
- has email addresses and roles


### AFRNIC: https://rdap.afrinic.net/rdap/

- no role information on any entities
- no name on org entity: https://rdap.afrinic.net/rdap/entity/ORG-WCL1-AFRINIC


### APNIC: https://rdap.apnic.net/autnum/7521
- org name in remarks
- no registrant role
- no email addresses
- appears all entities are 404 not found
  * https://rdap.apnic.net/autnum/7521 to> http://rdap.apnic.net/entity/JP00001394 is a 404 not found.

* changed while I was looking at it
* check why the entity recurse went to http


### LACNIC: https://rdap.lacnic.net/bootstrap/

  NIC.br:
    email addresses on IPv4 server, no email addresses on IPv6 server
    * emailed
