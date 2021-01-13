from bisect import bisect_left, bisect_right


class AsnService:
    """Defines a service URL to lookup an ASN from."""

    def __init__(self, url, start_asn, end_asn=None):
        self.url = url
        self.start_asn = start_asn
        # use start_asn if it's a single value
        self.end_asn = end_asn or start_asn

    def __str__(self):
        return f"{self.start_asn}-{self.end_asn} {self.url}"


class AsnTree:
    """Defines a search tree to find service URLs for ASNs."""

    def __init__(self, data=None):
        self._keys = []
        self._items = []

        if data:
            self.load_data(data)

    def __len__(self):
        return len(self._items)

    def __iter__(self):
        return iter(self._items)

    def load_data(self, data):
        """Loads data from iana format."""
        for service in data["services"]:
            # only get primary URL
            url = service[1][0].rstrip("/")
            for asn_range in service[0]:
                self.insert(url, asn_range)

    def insert(self, url, asn_range):
        "Insert a service locator record."
        top = None
        try:
            bottom, top = map(int, asn_range.split("-"))
        except ValueError:
            bottom = int(asn_range)
        service = AsnService(url, bottom, top)

        i = bisect_left(self._keys, bottom)
        self._keys.insert(i, bottom)
        self._items.insert(i, service)
        return service

    def get_service(self, asn):
        "Return service for asn.  Raise LookupError if not found."
        i = bisect_right(self._keys, asn)
        # correct record will be the previous one
        service = self._items[i - 1]
        if service and asn >= service.start_asn and asn <= service.end_asn:
            return service
        raise KeyError(f"No service found for AS{asn}")


# def load_asn_db(directory):
#    if
