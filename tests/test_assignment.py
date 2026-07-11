import datetime
import os
from unittest.mock import patch

import pytest
import requests

from rdap.assignment import RIRAssignmentLookup
from rdap.exceptions import RIRAssignmentError

DATA_DIR = os.path.join(os.path.dirname(__file__), "data", "assignment")


class TestLookup(RIRAssignmentLookup):
    def download_data(self, rir, file_path, cache_days):
        setattr(self, "_downloaded_{rir}", file_path)


def _read_fixture(name):
    with open(os.path.join(DATA_DIR, name)) as fh:
        return fh.read()


def test_lookup():
    lookup = TestLookup()
    lookup.load_data(DATA_DIR)

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


GOOD_DATA = _read_fixture("sample-complete")
TRUNCATED_DATA = _read_fixture("sample-truncated")


def test_expected_asn_count_and_record_count():
    lookup = RIRAssignmentLookup()
    assert lookup.expected_asn_count(GOOD_DATA) == 3
    assert lookup.count_asn_records(GOOD_DATA) == 3
    # no summary line -> None (fixtures / older files)
    assert lookup.expected_asn_count("ripencc|NL|asn|100|1|x|allocated|u\n") is None
    # summary line with a non-numeric count -> None
    assert lookup.expected_asn_count("ripencc|*|asn|*|notanumber|summary\n") is None


def test_validate_content_accepts_complete_data():
    RIRAssignmentLookup().validate_content("ripencc", GOOD_DATA)


def test_validate_content_rejects_truncated_data():
    with pytest.raises(RIRAssignmentError, match="truncated"):
        RIRAssignmentLookup().validate_content("ripencc", TRUNCATED_DATA)


def test_validate_content_rejects_empty_data():
    with pytest.raises(RIRAssignmentError, match="empty"):
        RIRAssignmentLookup().validate_content("ripencc", "   \n")


def test_validate_content_rejects_non_delegated_body():
    # a 200 response that is not delegated-stats data (e.g. a proxy/error page)
    html = "<html><body>503 Service Unavailable</body></html>\n"
    with pytest.raises(RIRAssignmentError, match="no asn records"):
        RIRAssignmentLookup().validate_content("ripencc", html)


def test_download_writes_good_data(tmp_path):
    lookup = RIRAssignmentLookup()
    dest = tmp_path / "delegated-ripencc-extended-latest"

    resp = requests.Response()
    resp.status_code = 200
    resp._content = GOOD_DATA.encode()
    with patch("rdap.assignment.requests.get", return_value=resp):
        lookup.download_data("ripencc", str(dest))

    assert dest.read_text() == GOOD_DATA
    # no temp file left behind
    assert list(tmp_path.glob("*.tmp")) == []


def test_download_truncated_keeps_existing_cache(tmp_path):
    lookup = RIRAssignmentLookup()
    dest = tmp_path / "delegated-ripencc-extended-latest"
    dest.write_text(GOOD_DATA)
    # force re-download by ageing the file past the window
    old = 1000
    os.utime(dest, (old, old))

    resp = requests.Response()
    resp.status_code = 200
    resp._content = TRUNCATED_DATA.encode()
    with patch("rdap.assignment.requests.get", return_value=resp):
        lookup.download_data("ripencc", str(dest), cache_days=1)

    # the good cache is preserved, not overwritten by the truncated fetch
    assert dest.read_text() == GOOD_DATA


def test_download_http_error_without_cache_raises(tmp_path):
    lookup = RIRAssignmentLookup()
    dest = tmp_path / "delegated-ripencc-extended-latest"

    resp = requests.Response()
    resp.status_code = 500
    with (
        patch("rdap.assignment.requests.get", return_value=resp),
        pytest.raises(RIRAssignmentError),
    ):
        lookup.download_data("ripencc", str(dest))
    assert not dest.exists()


def test_download_refetches_corrupt_fresh_cache(tmp_path):
    # a within-window but corrupt cache must be re-downloaded (self-heal),
    # not trusted
    lookup = RIRAssignmentLookup()
    dest = tmp_path / "delegated-ripencc-extended-latest"
    dest.write_text(TRUNCATED_DATA)  # fresh (just written) but invalid

    resp = requests.Response()
    resp.status_code = 200
    resp._content = GOOD_DATA.encode()
    with patch("rdap.assignment.requests.get", return_value=resp) as mocked_get:
        lookup.download_data("ripencc", str(dest), cache_days=1)
        mocked_get.assert_called_once()

    assert dest.read_text() == GOOD_DATA


def test_download_failure_with_corrupt_cache_raises(tmp_path):
    # fetch fails AND the only cache on disk is corrupt -> no usable data, raise
    lookup = RIRAssignmentLookup()
    dest = tmp_path / "delegated-ripencc-extended-latest"
    dest.write_text(TRUNCATED_DATA)
    os.utime(dest, (1000, 1000))  # expired

    resp = requests.Response()
    resp.status_code = 200
    resp._content = TRUNCATED_DATA.encode()  # fetch also truncated
    with (
        patch("rdap.assignment.requests.get", return_value=resp),
        pytest.raises(RIRAssignmentError),
    ):
        lookup.download_data("ripencc", str(dest), cache_days=1)


def test_download_cleans_up_temp_on_replace_failure(tmp_path):
    # if the atomic replace fails, the temp file must not be left behind
    lookup = RIRAssignmentLookup()
    dest = tmp_path / "delegated-ripencc-extended-latest"

    resp = requests.Response()
    resp.status_code = 200
    resp._content = GOOD_DATA.encode()
    with (
        patch("rdap.assignment.requests.get", return_value=resp),
        patch("rdap.assignment.os.replace", side_effect=OSError("boom")),
        pytest.raises(OSError),
    ):
        lookup.download_data("ripencc", str(dest))

    assert list(tmp_path.glob("*.tmp")) == []


def test_cache_not_expired_skips_download(tmp_path):
    lookup = RIRAssignmentLookup()
    dest = tmp_path / "delegated-ripencc-extended-latest"
    dest.write_text(GOOD_DATA)  # freshly written -> within window

    with patch("rdap.assignment.requests.get") as mocked_get:
        lookup.download_data("ripencc", str(dest), cache_days=1)
        mocked_get.assert_not_called()


def test_cache_expired_uses_seconds_not_floored_days(tmp_path):
    lookup = RIRAssignmentLookup()
    dest = tmp_path / "delegated-ripencc-extended-latest"
    dest.write_text(GOOD_DATA)
    # 1.5 days old: floored .days == 1 (old check would NOT refresh), but this
    # is older than cache_days=1 (86400s) so it must be treated as expired
    stale = (datetime.datetime.now() - datetime.timedelta(days=1, hours=12)).timestamp()
    os.utime(dest, (stale, stale))
    assert lookup._cache_expired(str(dest), cache_days=1) is True
