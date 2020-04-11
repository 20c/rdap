def test_rdap_ip_lookup(rdapc):
    query = "1.1.1.1"
    obj = rdapc.get_ip(query)
    assert obj.data

    # test get duduction
    assert obj.data == rdapc.get(query).data
