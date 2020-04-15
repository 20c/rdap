def sort_data(data):
    """ Sorts data returned from rdap queries for comparing. """
    for entity in data.get("entities", []):
        if "roles" in entity:
            entity["roles"].sort()
            print(entity["roles"])


def test_rdap_ip_lookup(rdapc):
    query = "1.1.1.1"
    ip = rdapc.get_ip(query)
    assert ip.data
    sort_data(ip.data)

    # test get deduction
    obj = rdapc.get(query)
    assert obj.data
    sort_data(obj.data)

    assert type(ip) == type(obj)
    assert ip.data == obj.data
