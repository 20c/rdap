
def test_rdap_asn_lookup(rdapc):
    obj = rdapc.get_ip("1.1.1.1")
    assert obj.data
