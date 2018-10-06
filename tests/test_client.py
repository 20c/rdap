
from rdap import client


def test_strip_auth_none():
    url = "https://example.com/entity/20C"

    # test no auth
    assert url == client.strip_auth(url)


def test_strip_auth():
    url = "https://example.com/entity/20C/?key=value"

    # test no auth
    assert url == client.strip_auth(url)

    # test only auth
    assert url == client.strip_auth(url + "&apikey=12345")
