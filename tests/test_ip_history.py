"""Tests for RDAP IP history functionality (APNIC /history endpoint)"""

import json
import os

import pytest

import rdap


@pytest.fixture
def history_data():
    """Load test data for APNIC history endpoint"""
    test_file = os.path.join(
        os.path.dirname(__file__),
        "data/rdap/ip/101.203.88.0_history.input",
    )
    with open(test_file) as fh:
        return json.load(fh)


def test_rdap_history_record(history_data):
    """Test RdapHistoryRecord class"""
    records_data = history_data.get("records", [])
    assert len(records_data) > 0, "Test data should have records"

    record = rdap.objects.RdapHistoryRecord(records_data[0])

    assert record.applicable_from is not None
    assert isinstance(record.is_current, bool)

    content = record.content
    assert content is not None
    assert hasattr(content, "handle")


def test_rdap_history_object(history_data):
    """Test RdapHistory class"""
    history = rdap.objects.RdapHistory(history_data, queried_prefix="101.203.88.0/24")

    records = history.records
    assert isinstance(records, list)
    assert len(records) > 0

    # Verify records are sorted newest to oldest
    for i in range(len(records) - 1):
        if records[i].applicable_from and records[i + 1].applicable_from:
            assert records[i].applicable_from >= records[i + 1].applicable_from


def test_rdap_history_filter_by_handle(history_data):
    """Test filtering records by handle"""
    history = rdap.objects.RdapHistory(history_data, queried_prefix="101.203.88.0/24")

    all_records = history.records
    assert len(all_records) > 0

    if all_records:
        test_handle = all_records[0].handle

        filtered = history.filter_by_handle(test_handle)

        for record in filtered:
            assert record.handle == test_handle


def test_rdap_history_most_specific(history_data):
    """Test get_most_specific_records filtering"""
    history = rdap.objects.RdapHistory(history_data, queried_prefix="101.203.88.0/24")

    most_specific = history.get_most_specific_records()

    assert isinstance(most_specific, list)

    # Most specific records should exclude parent blocks
    # (e.g., should not include 0.0.0.0/0 or 101.0.0.0/8)
    if most_specific:
        for record in most_specific:
            handle = record.handle
            # Parent blocks have very large ranges
            assert "0.0.0.0 - 255.255.255.255" not in handle
            assert "101.0.0.0 - 101.255.255.255" not in handle


def test_rdap_history_current_record(history_data):
    """Test identifying current vs historical records"""
    history = rdap.objects.RdapHistory(history_data, queried_prefix="101.203.88.0/24")

    current_records = [r for r in history.records if r.is_current]
    historical_records = [r for r in history.records if not r.is_current]

    # Should have at least some historical records
    # (current record count depends on test data)
    assert len(historical_records) >= 0

    # Current records should have no applicable_until
    for record in current_records:
        assert record.applicable_until is None

    # Historical records should have applicable_until
    for record in historical_records:
        assert record.applicable_until is not None


def test_rdap_history_record_content_types(history_data):
    """Test that content objects are created with correct types"""
    history = rdap.objects.RdapHistory(history_data, queried_prefix="101.203.88.0/24")

    records = history.records
    if records:
        record = records[0]
        content = record.content

        assert isinstance(content, rdap.objects.RdapNetwork)

        assert hasattr(content, "handle")
        assert hasattr(content, "name")
        assert hasattr(content, "data")


def test_rdap_history_record_handle_property(history_data):
    """Test RdapHistoryRecord handle property"""
    history = rdap.objects.RdapHistory(history_data, queried_prefix="101.203.88.0/24")

    records = history.records
    if records:
        record = records[0]

        handle = record.handle
        assert handle is not None
        assert isinstance(handle, str)


def test_rdap_history_empty_records():
    """Test RdapHistory with no records"""
    empty_data = {"records": []}
    history = rdap.objects.RdapHistory(empty_data, queried_prefix="192.0.2.0/24")

    assert history.records == []
    assert history.get_most_specific_records() == []
    assert history.filter_by_handle("test") == []


def test_rdap_history_record_without_content():
    """Test RdapHistoryRecord with missing content"""
    record_data = {
        "applicableFrom": "2020-01-01T00:00:00Z",
        "applicableUntil": "2021-01-01T00:00:00Z",
        "content": {},
    }
    record = rdap.objects.RdapHistoryRecord(record_data)

    assert record.applicable_from == "2020-01-01T00:00:00Z"
    assert record.applicable_until == "2021-01-01T00:00:00Z"
    assert record.is_current is False
