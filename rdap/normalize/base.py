"""Rdap data parsers for ARIN data"""

import ipaddress
from datetime import datetime
from typing import Dict, List, Optional, Union

import phonenumbers

import rdap.schema.rdap as schema
from rdap.context import RdapRequestContext, RdapRequestState, rdap_request
from rdap.normalize import geo
from rdap.schema.normalized import DNSSEC, Contact, Nameserver

__all__ = [
    "Handler",
]


class Handler:
    def locations_from_entity(self, entity: schema.Entity) -> List[str]:
        """Will parse an address from an entity

        Will return the address if it can be found, otherwise None
        """
        # address will be through entities
        # looking for vcardArray with ["adr", {"label": address}, "text"] to
        # establish the address entry

        locations = []

        dates = self.dates(entity.events)

        updated = dates["updated"]

        for vcard in entity.vcardArray[1:]:
            for vcard_entry in vcard:
                if vcard_entry[0] == "adr":
                    address = vcard_entry[1].get("label")
                    locations.append(geo.normalize(address, updated))

        if entity.entities:
            for _entity in entity.entities:
                locations.extend(self.locations_from_entity(_entity))

        # remove dupes
        locations = list(set(locations))

        return locations

    def locations(
        self,
        entity: Union[schema.AutNum, schema.IPNetwork, schema.Domain],
    ) -> List[str]:
        """Will parse an address from an object

        Will return the address if it can be found, if no address
        can be found, will return None
        """
        locations = []

        for _entity in entity.entities:
            locations.extend(self.locations_from_entity(_entity))

        # remove dupes
        locations = list(set(locations))

        # sort by address
        locations.sort(key=lambda x: x.address)

        return locations

    def contacts_from_entity(
        self,
        entity: schema.Entity,
        deep: bool = True,
    ) -> List[Contact]:
        """Will parse contacts from an entity

        Will return a list of contacts if it can be found, otherwise an empty list

        vcard entriews that are considered:

        ["email", {}, "text", email]
        ["tel", {}, "text", phone]
        ["fn", {}, "text", name]

        A contact is considered if `fn` and either of `email` or `tel` is present

        If deep is set to True, will also check nessted entities.
        """
        contacts = []

        for vcard in entity.vcardArray[1:]:
            contact = Contact(
                name="",
                roles=getattr(entity, "roles", []) or [],
                **self.dates(entity.events),
            )
            for vcard_entry in vcard:
                if vcard_entry[0] == "fn":
                    contact.name = vcard_entry[3]
                if vcard_entry[0] == "email":
                    contact.email = vcard_entry[3]
                if vcard_entry[0] == "tel":
                    contact.phone = vcard_entry[3]
                    try:
                        phone_number = phonenumbers.parse(contact.phone, None)
                        contact.phone = phonenumbers.format_number(
                            phone_number,
                            phonenumbers.PhoneNumberFormat.INTERNATIONAL,
                        )
                    except phonenumbers.phonenumberutil.NumberParseException:
                        # TODO: setting to allow for invalid phone numbers?
                        contact.phone = None

                if contact.name and (contact.email or contact.phone):
                    contacts.append(contact)

            if deep and getattr(entity, "entities", None):
                for _entity in entity.entities:
                    contacts.extend(self.contacts_from_entity(_entity, deep=True))

        # remove dupes
        contacts = list(set(contacts))

        self.recurse_contacts(entity, contacts, entity.roles)

        return contacts

    def contacts(
        self,
        entity: Union[schema.AutNum, schema.IPNetwork, schema.Domain],
        deep: bool = True,
    ) -> List[Contact]:
        """Will parse contacts from an object

        Will return a list of contacts if it can be found, otherwise an empty list

        If deep is set to True, will also check nessted entities.
        """
        contacts = []

        for _entity in entity.entities:
            contacts.extend(self.contacts_from_entity(_entity, deep=deep))

        # remove dupes
        contacts = list(set(contacts))

        # now cycle through and combine contacts
        #
        # check `name`, `phone` and `email` and if all three
        # are the same, combine the roles

        combined_contacts = {}

        # sort by name and email
        contacts = sorted(contacts, key=lambda x: (x.name or "", x.email or ""))

        for _contact in contacts:
            key = f"{_contact.name}"

            if key in combined_contacts:
                combined_contacts[key].roles.extend(_contact.roles)
                if (
                    not combined_contacts[key].email
                    and _contact.email
                    and _contact.phone == combined_contacts[key].phone
                ):
                    combined_contacts[key].email = _contact.email
                if (
                    not combined_contacts[key].phone
                    and _contact.phone
                    and _contact.email == combined_contacts[key].email
                ):
                    combined_contacts[key].phone = _contact.phone
            else:
                combined_contacts[key] = _contact

        contacts = list(combined_contacts.values())

        # sort roles
        for contact in contacts:
            contact.roles = sorted(list(set(contact.roles)))

        return contacts

    def recurse_contacts(
        self,
        entity: schema.Entity,
        contacts: List[Contact],
        roles: List[str],
    ) -> List[Contact]:
        request_state: RdapRequestState = rdap_request.get()
        client = request_state.client

        # if role is in settings to recurse, try to do a lookup
        if entity.handle and client:
            handle_url = entity.self_link
            if not handle_url:
                handle_url = client.get_entity_url(entity.handle)

            if not client.recurse_roles.isdisjoint(roles):
                with RdapRequestContext(url=handle_url, client=client) as ctx:
                    contacts.extend(
                        [
                            Contact(**contact)
                            for contact in ctx.get("entity", entity.handle).get(
                                "contacts",
                                [],
                            )
                        ],
                    )

    def org_name_from_entity(self, entity: schema.Entity) -> Optional[str]:
        """Will parse an org name from an entity

        Will return the org name if it can be found, otherwise None
        """
        # org name will be through entities
        # looking for vcardArray with ["kind", {}, "text", org] to
        # establish the org entry
        #
        # in the same vcardArray, looking for ["fn", {}, "text", name]

        kind_is_org = False
        org_name = None

        for vcard in entity.vcardArray[1:]:
            for vcard_entry in vcard:
                if vcard_entry[0] == "kind" and vcard_entry[3] == "org":
                    kind_is_org = True
                if vcard_entry[0] == "fn":
                    org_name = vcard_entry[3]

        if kind_is_org and org_name:
            return org_name

        return None

    def org_name(
        self,
        entity: Union[schema.AutNum, schema.IPNetwork, schema.Domain],
    ) -> Optional[str]:
        """Will parse an org name from an object

        Will return the org name if it can be found, if no org name
        can be found, will return entity name or None
        """
        for _entity in entity.entities:
            name = self.org_name_from_entity(_entity)
            if name:
                return name

        return entity.name or None

    def prefix(
        self,
        ip_network: schema.IPNetwork,
    ) -> Union[ipaddress.IPv4Network, ipaddress.IPv6Network, None]:
        """Will return the CIDR of an IPNetwork object
        "cidr0_cidrs" : [ {
            "v4prefix" : "206.41.110.0",
            "length" : 24
        } ],
        """
        if not ip_network.cidr0_cidrs:
            # try if handle can be coerced into a prefix

            if ip_network.handle:
                try:
                    return ipaddress.ip_network(ip_network.handle)
                except ValueError:
                    pass

            return None

        cidr = ip_network.cidr0_cidrs[0]

        if "v4prefix" in cidr:
            return ipaddress.IPv4Network(f"{cidr['v4prefix']}/{cidr['length']}")

        if "v6prefix" in cidr:
            return ipaddress.IPv6Network(f"{cidr['v6prefix']}/{cidr['length']}")

        return None

    def ip_version(self, ip_network: schema.IPNetwork) -> Union[int, None]:
        """Will return the IP version of an IPNetwork object"""
        prefix = self.prefix(ip_network)

        if prefix:
            return prefix.version

        ip_version = ip_network.ipVersion

        if ip_version == "v4":
            return 4
        if ip_version == "v6":
            return 6

        return None

    def parent_prefix(
        self,
        ip_network: schema.IPNetwork,
    ) -> Union[ipaddress.IPv4Network, ipaddress.IPv6Network, None]:
        """Parent network prefix from `parentHandle`

        "parentHandle" : "NET-206-0-0-0-0",
        """
        if not ip_network.parentHandle:
            return None

        # Extract the IP address part from the parentHandle
        ip_parts = ip_network.parentHandle.split("-")[1:-1]

        # Reconstruct the IP address string
        ip_str = ".".join(ip_parts)

        # Determine the appropriate prefix length based on the number of non-zero octets
        non_zero_octets = sum(1 for part in ip_parts if part != "0")
        prefix_length = non_zero_octets * 8

        # Construct the CIDR notation
        cidr = f"{ip_str}/{prefix_length}"

        try:
            # Attempt to create an IP network object
            return ipaddress.ip_network(cidr, strict=False)
        except ValueError:
            # If the IP address is invalid, return None
            return None

    def secure_dns(self, domain: schema.Domain) -> DNSSEC:
        """Will determine if the domain has secure DNS

        This is determined by the `secureDNS` object

        If `delegationSigned` or `zeroSigned` is True, will return secure

        If both are False, will return insecure

        If secureDNS is not present, or both are None, will return unknown
        """
        if not domain.secureDNS:
            return DNSSEC.unknown

        if (
            domain.secureDNS.delegationSigned is None
            and domain.secureDNS.zeroSigned is None
        ):
            return DNSSEC.unknown

        if domain.secureDNS.delegationSigned or domain.secureDNS.zeroSigned:
            return DNSSEC.secure

        return DNSSEC.insecure

    def nameservers(self, domain: schema.Domain) -> List[Nameserver]:
        """Returns normalized nameservers from a domain object"""
        nameservers = []

        for nameserver in domain.nameservers:
            nameservers.append(Nameserver(host=nameserver.ldhName))

        return nameservers

    def dates(self, events: List[schema.Event]) -> Dict[str, str]:
        """Return the created and updated dates from the events"""
        created = None
        updated = None

        for event in events:
            if event.eventAction == "registration":
                created: datetime = event.eventDate
            if event.eventAction == "last changed":
                updated: datetime = event.eventDate

        # set utc timezone if no timezone is present
        # created and du

        if created and not created.tzinfo:
            created = created.replace(tzinfo=datetime.timezone.utc)

        if updated and not updated.tzinfo:
            updated = updated.replace(tzinfo=datetime.timezone.utc)

        return {"created": created, "updated": updated}
