from rdap.exceptions import RdapHTTPError, RdapNotFoundError
from rdap.normalize import normalize


def rir_from_domain(domain):
    """Gets the RIR from a URL or domain, if possible"""
    try:
        for rir in ["arin", "apnic", "afrinic", "lacnic", "ripe"]:
            if rir in domain:
                return rir

        if "nic.br" in domain:
            return "lacnic"

    except Exception:
        return None


class RdapObject:
    """RDAP base object, allows for lazy parsing"""

    def __init__(self, data, rdapc=None):
        self._rdapc = rdapc
        self._data = data
        self._parsed = {}

    @property
    def data(self):
        return self._data

    @property
    def name(self):
        return self.parsed()["name"]

    @property
    def handle(self):
        return self._data["handle"]

    @property
    def emails(self):
        return self.parsed()["emails"]

    @property
    def org_name(self):
        return self.parsed()["org_name"]

    @property
    def org_address(self):
        return self.parsed()["org_address"]

    @property
    def kind(self):
        return self.parsed()["kind"]

    def parsed(self):
        """Returns parsed dict"""
        if not self._parsed:
            self._parse()
        return self._parsed

    def _parse_vcard(self, data):
        """Iterates over current level's vcardArray and gets data"""
        vcard = {}

        for row in data.get("vcardArray", [0])[1:]:
            for typ in row:
                if typ[0] in ["version"]:
                    continue
                if typ[0] == "email":
                    vcard.setdefault("emails", set()).add(typ[3].strip().lower())
                elif typ[0] == "fn" or typ[0] == "kind":
                    vcard[typ[0]] = typ[3].strip()
                elif typ[0] == "adr":
                    # WORKAROUND ARIN uses label in the extra field
                    adr = typ[1].get("label", "").strip()
                    if not adr:
                        # rest use the text field
                        adr = "\n".join([str(item) for item in typ[3]]).strip()
                    if adr:
                        vcard["adr"] = adr
        return vcard

    def _parse_entity_self_link(self, entity):
        for link in entity.get("links", []):
            if link["rel"] == "self":
                return link["href"]
        return None

    def _parse(self):
        """Parses data into our format, and use entities for address info ?"""
        name = self._data.get("name", "")
        # emails done with a set to eat duplicates
        emails = set()
        org_name = ""
        org_address = ""
        org_name_final = False
        org_address_final = False

        for ent in self._data.get("entities", []):
            vcard = self._parse_vcard(ent)
            emails |= vcard.get("emails", set())
            roles = ent.get("roles", [])
            kind = vcard.get("kind", "")
            handle = ent.get("handle", None)
            # try for link to 'self', if registry doesn't supply it, fall back to creating it.
            handle_url = self._parse_entity_self_link(ent)
            if not handle_url:
                handle_url = self._rdapc.get_entity_url(handle)

            if "registrant" in roles:
                if "fn" in vcard and not org_name_final:
                    org_name = vcard["fn"]
                    if "org" in kind:
                        org_name_final = True
                if "adr" in vcard and not org_address_final:
                    org_address = vcard["adr"]
                    if "org" in kind:
                        org_address_final = True

            # check nested entities
            for nent in ent.get("entities", []):
                vcard = self._parse_vcard(nent)
                emails |= vcard.get("emails", set())

            # if role is in settings to recurse, try to do a lookup
            if (
                handle
                and self._rdapc
                and not self._rdapc.recurse_roles.isdisjoint(roles)
            ):
                try:
                    rdata = self._rdapc.get_data(handle_url)
                    vcard = self._parse_vcard(rdata)
                    emails |= vcard.get("emails", set())

                # check for HTTP Errors to ignore
                except RdapHTTPError:
                    if not self._rdapc.config.get("ignore_recurse_errors"):
                        raise

        # WORKAROUND APNIC keeps org info in remarks
        if "apnic" in self._data.get("port43", ""):
            try:
                for rem in self._data["remarks"]:
                    if rem["title"] == "description":
                        if org_name:
                            org_name += ", "
                        org_name += rem["description"][0]
                        break
            except KeyError:
                pass

        # RIPE keeps org info in remarks
        elif "ripe" in self._data.get("port43", ""):
            try:
                for rem in self._data["remarks"]:
                    if rem["description"]:
                        if org_name:
                            org_name += ", "
                        org_name += rem["description"][0]
                        break
            except KeyError:
                pass

        self._parsed = {
            "name": name,
            "emails": sorted(emails),
            "org_name": org_name,
            "org_address": org_address,
        }

    def get_rir(self):
        """Gets the RIR for the object, if possible"""
        try:
            if "port43" in self._data and (
                rir := rir_from_domain(self._data.get("port43"))
            ):
                return rir

            if (
                self._rdapc
                and self._rdapc.last_req_url
                and (rir := rir_from_domain(self._rdapc.last_req_url))
            ):
                return rir

        except Exception:
            return None


class RdapAsn(RdapObject):
    """access interface for lazy parsing of RDAP looked up aut-num objects"""

    def __init__(self, data, rdapc=None):
        # check for ASN range, meaning it's delegated and unallocated
        if data:
            start = data.get("startAutnum", None)
            end = data.get("endAutnum", None)
            if start and end and start != end:
                raise RdapNotFoundError(
                    f"Query returned a block ({start} - {end}), AS is reported not allocated",
                )

        super().__init__(data, rdapc)

    @property
    def normalized(self) -> dict:
        return normalize(self._data, self.get_rir(), "autnum")


class RdapNetwork(RdapObject):
    def __init__(self, data, rdapc=None):
        super().__init__(data, rdapc)

    @property
    def normalized(self) -> dict:
        return normalize(self._data, self.get_rir(), "ip")


class RdapDomain(RdapObject):
    def __init__(self, data, rdapc=None):
        super().__init__(data, rdapc)

    @property
    def normalized(self) -> dict:
        return normalize(self._data, self.get_rir(), "domain")


class RdapEntity(RdapObject):
    def __init__(self, data, rdapc=None):
        super().__init__(data, rdapc)

    @property
    def normalized(self) -> dict:
        return normalize(self._data, self.get_rir(), "entity")


class RdapHistoryRecord:
    """Represents a single historical record from an RDAP history query.

    Each record contains:
    - applicableFrom: timestamp when this record became active
    - applicableUntil: timestamp when this record was superseded (None if current)
    - content: the RDAP object data at that point in time
    """

    def __init__(self, record_data, rdapc=None):
        self._rdapc = rdapc
        self._record_data = record_data
        self._content_obj = None

    @property
    def applicable_from(self) -> str | None:
        """Timestamp when this record became active"""
        return self._record_data.get("applicableFrom")

    @property
    def applicable_until(self) -> str | None:
        """Timestamp when this record was superseded (None if current)"""
        return self._record_data.get("applicableUntil")

    @property
    def is_current(self) -> bool:
        """Returns True if this is the currently active record"""
        return self.applicable_until is None

    @property
    def content(
        self,
    ) -> RdapNetwork | RdapAsn | RdapDomain | RdapEntity | RdapObject | None:
        """Returns the parsed RDAP object for this historical record.
        Lazily creates an RdapNetwork object from the content data.
        """
        if not self._content_obj:
            content_data = self._record_data.get("content", {})
            if content_data:
                object_class = content_data.get("objectClassName")
                if object_class == "ip network":
                    self._content_obj = RdapNetwork(content_data, self._rdapc)
                elif object_class == "autnum":
                    self._content_obj = RdapAsn(content_data, self._rdapc)
                elif object_class == "domain":
                    self._content_obj = RdapDomain(content_data, self._rdapc)
                elif object_class == "entity":
                    self._content_obj = RdapEntity(content_data, self._rdapc)
                else:
                    self._content_obj = RdapObject(content_data, self._rdapc)
        return self._content_obj

    @property
    def handle(self) -> str | None:
        """Shortcut to get the handle from content"""
        return self._record_data.get("content", {}).get("handle")

    @property
    def data(self) -> dict:
        """Returns the raw record data"""
        return self._record_data


class RdapHistory:
    """Represents the complete history response from an RDAP history query.

    Contains a list of RdapHistoryRecord objects sorted by time.
    Provides filtering options to get specific records (exact match, parent blocks, etc.)
    """

    def __init__(self, data, rdapc=None, queried_prefix=None):
        """Initialize RdapHistory object.

        Args:
            data: Raw RDAP history response data
            rdapc: RdapClient instance
            queried_prefix: The prefix that was queried (for filtering purposes)

        """
        self._rdapc = rdapc
        self._data = data
        self._queried_prefix = queried_prefix
        self._records = None

    @property
    def data(self) -> dict:
        """Returns raw history data"""
        return self._data

    @property
    def records(self) -> list[RdapHistoryRecord]:
        """Returns all historical records as RdapHistoryRecord objects.
        Records are sorted newest to oldest (reverse chronological).
        """
        if self._records is None:
            records_data = self._data.get("records", [])
            self._records = [
                RdapHistoryRecord(record, self._rdapc) for record in records_data
            ]
            self._records.sort(key=lambda r: r.applicable_from or "", reverse=True)
        return self._records

    def filter_by_handle(self, handle: str) -> list[RdapHistoryRecord]:
        """Filter records by exact handle match.

        Args:
            handle: The handle to filter by (e.g., "101.203.88.0 - 101.203.95.255")

        Returns:
            List of RdapHistoryRecord objects matching the handle

        """
        return [r for r in self.records if r.handle == handle]

    def get_most_specific_records(self) -> list[RdapHistoryRecord]:
        """Returns only the records for the most specific (smallest) IP block.
        This filters out parent/larger allocations.

        Returns:
            List of RdapHistoryRecord objects for the most specific block

        """
        if not self.records:
            return []

        # Find the record with the smallest IP range (most specific)
        # We'll use the current record (applicableUntil == None) to determine this
        current_records = [r for r in self.records if r.is_current]

        if not current_records:
            current_records = [self.records[0]] if self.records else []

        if current_records:
            most_specific_handle = current_records[0].handle
            return self.filter_by_handle(most_specific_handle)

        return []

    def get_current_record(self) -> RdapHistoryRecord | None:
        """Returns the currently active record (applicableUntil is None).

        Returns:
            RdapHistoryRecord object or None if no current record found

        """
        current = [r for r in self.records if r.is_current]
        return current[0] if current else None
