
def test_rdap_domain_lookup(rdapc):
    rdapc.url = "https://rdap.test.norid.no"
    query = "norid-test.no"
    obj = rdapc.get_domain(query)
    assert obj.data

    # test get duduction
    assert obj.data == rdapc.get(query).data
