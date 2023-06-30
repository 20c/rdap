import os

from rdap.assignment import RIRAssignmentLookup


class TestLookup(RIRAssignmentLookup):
    def download_data(self, rir, file_path, cache_days):
        setattr(self, "_downloaded_{rir}", file_path)


def test_lookup():
    lookup = TestLookup()
    path = os.path.join(os.path.dirname(__file__), "data", "assignment")
    lookup.load_data(path)

    # no info
    assert lookup.get_status(8771) is None

    # afrinic
    assert lookup.get_status(8524) == "allocated"
    assert lookup.get_status(8770) == "available"

    # apnic
    assert lookup.get_status(1781) == "allocated"

    # arin
    assert lookup.get_status(63311) == "assigned"
    assert lookup.get_status(63317) == "reserved"
    assert lookup.get_status(63360) == "assigned"
    assert lookup.get_status(63361) == "assigned"
    assert lookup.get_status(63362) is None

    # lacnic
    assert lookup.get_status(6193) == "allocated"
    assert lookup.get_status(6148) == "available"

    # ripe
    assert lookup.get_status(7) == "allocated"
