from builtins import object


class RdapObject(object):
    """
    RDAP base object, allows for lazy parsing
    """

    def __init__(self, data, rdapc=None):
        self._rdapc = rdapc
        self._data = data
        self._parsed = dict()

    @property
    def data(self):
        return self._data

    @property
    def name(self):
        return self.parsed()['name']

    @property
    def handle(self):
        return self._data['handle']

    @property
    def emails(self):
        return self.parsed()['emails']

    @property
    def org_name(self):
        return self.parsed()['org_name']

    @property
    def org_address(self):
        return self.parsed()['org_address']

    def parsed(self):
        """
        returns parsed dict
        """
        if not self._parsed:
            self._parse()
        return self._parsed


class RdapAsn(RdapObject):
    """
    access interface for lazy parsing of RDAP looked up aut-num objects
    """
    def __init__(self, data, rdapc=None, **kwargs):
        super(RdapAsn, self).__init__(data, rdapc, **kwargs)

    def _parse_vcard(self, data):
        """
        iterates over current level's vcardArray and gets data
        """
        vcard = dict()

        for row in data.get('vcardArray', [0])[1:]:
            for typ in row:
                if typ[0] in ['version']:
                    continue
                elif typ[0] == 'email':
                    vcard.setdefault('emails', set()).add(
                        typ[3].strip().lower())
                elif typ[0] == 'fn':
                    vcard[typ[0]] = typ[3].strip()
                elif typ[0] == 'adr':
                    # WORKAROUND ARIN uses label in the extra field
                    adr = typ[1].get('label', '').strip()
                    if not adr:
                        # rest use the text field
                        adr = "\n".join(typ[3]).strip()
                    if adr:
                        vcard['adr'] = adr
        return vcard

    def _parse(self):
        """ parses data into our format """
        name = self._data.get('name', '')
        # emails done with a set to eat duplicates
        emails = set()
        org_name = ''
        org_address = ''

        for ent in self._data['entities']:
            vcard = self._parse_vcard(ent)
            emails |= vcard.get('emails', set())
            roles = ent.get('roles', [])
            handle = ent.get('handle', None)

            if 'registrant' in roles:
                if 'fn' in vcard:
                    org_name = vcard['fn']
                if 'adr' in vcard:
                    org_address = vcard['adr']

            # check nested entities
            for nent in ent.get('entities', []):
                vcard = self._parse_vcard(nent)
                emails |= vcard.get('emails', set())

            # if role is in settings to recurse, try to do a lookup
            if handle and self._rdapc:
                if not self._rdapc.recurse_roles.isdisjoint(roles):
                    rdata = self._rdapc.get_entity_data(handle)
                    vcard = self._parse_vcard(rdata)
                    emails |= vcard.get('emails', set())

        # WORKAROUND APNIC keeps org info in remarks
        if 'apnic' in self._data.get('port43', None):
            try:
                for rem in self._data['remarks']:
                    if rem["title"] == "description":
                        org_name = rem['description'][0]
                        break
            except KeyError:
                pass

        self._parsed = dict(
            name=name,
            emails=sorted(emails),
            org_name=org_name,
            org_address=org_address,
        )
