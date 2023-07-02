import rdap.objects


def test_rir_lookup(rdapc):
    assert rdap.objects.rir_from_domain("arin.net") == "arin"
    assert not rdap.objects.rir_from_domain("invalid")
