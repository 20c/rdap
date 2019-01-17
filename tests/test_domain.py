from rdap import RdapClient


def test_rdap_domain_lookup():
    rdapc = RdapClient()
    rdapc.url = "https://rdap.norid.no"
    query = "norid.no"
    obj = rdapc.get_domain(query)
    assert obj.data

    # test get duduction
    assert obj.data == rdapc.get(query).data
