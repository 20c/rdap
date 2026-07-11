import datetime
import logging
import os
from typing import ClassVar

import requests

from rdap.exceptions import RIRAssignmentError

logger = logging.getLogger(__name__)


class RIRAssignmentLookup:
    """Fetch RIR assignement status lists from ripe and lookup
    assignment per asn

    Files will be downloaded from  https://ftp.ripe.net/pub/stats/{rir}/delegated-{rir}-extended-latest
    """

    rir_lists: ClassVar = ["afrinic", "apnic", "arin", "lacnic", "ripencc"]

    def parse_data(self, line):
        """Parses a line from a data file and attempts to return the ASN
        and assignment status

        A line can parse multiple asns depending of the value in 5th
        column.

        Returns:
        - `None` if no asn and status could be parsed
        - `list<`dict`>` containing asns and status

        """
        parts = line.split("|")

        try:
            if parts[2] != "asn":
                return None
        except IndexError:
            return None

        try:
            asn = parts[3]
            count = int(parts[4])
            status = parts[6].strip()

            return [{"asn": int(asn) + i, "status": status} for i in range(count)]

        except IndexError:
            return None

    def expected_asn_count(self, text):
        """Number of asn records the file declares in its summary line
        (e.g. `ripencc|*|asn|*|48678|summary`), or `None` if absent. Compared
        to the records actually present to detect a truncated download.
        """
        for line in text.splitlines():
            parts = line.split("|")
            if (
                len(parts) >= 6
                and parts[1] == "*"
                and parts[2] == "asn"
                and parts[5].strip() == "summary"
            ):
                try:
                    return int(parts[4])
                except ValueError:
                    return None
        return None

    def count_asn_records(self, text):
        """Count asn record lines (excludes version/summary/malformed lines)."""
        count = 0
        for line in text.splitlines():
            parts = line.split("|")
            # record lines: registry|cc|asn|start|value|date|status[|ext...];
            # summary has 6 fields, version's 3rd field is a serial not "asn"
            if len(parts) < 7 or parts[2] != "asn":
                continue
            count += 1
        return count

    def validate_content(self, source, text):
        """Raise `RIRAssignmentError` if delegated-stats `text` is empty or
        truncated. Completeness is only checked when a summary count is present
        (`source` is a rir name or path, used for the error message).
        """
        if not text or not text.strip():
            raise RIRAssignmentError(f"RIR data for {source} is empty")

        actual = self.count_asn_records(text)
        if actual == 0:
            # non-empty but no asn records: e.g. a proxy/error page served 200
            raise RIRAssignmentError(f"RIR data for {source} has no asn records")

        expected = self.expected_asn_count(text)
        if expected is not None and actual < expected:
            raise RIRAssignmentError(
                f"RIR data for {source} looks truncated: "
                f"{actual} asn records present, summary declares {expected}"
            )

    def load_data(self, data_path=".", cache_days=1):
        """Reads RIR assignment data into memory

        This is called autoamtically by `get_status`

        This will download assignement status files from ripe if they dont
        exist yet or have expired. Initial call of this function will
        be signicantly slower than successive calls.

        For best performance it is recommended to use one RIRAssignmentLookup instance
        for multiple lookups.

        Argrument(s):

        - data_path (`str`): directory path to where downloaded files are to be saved
        - cache_days (`int`): maximum age of downloaded files before they will be
            downloaded again

        Raises `RIRAssignmentError` rather than silently loading partial data
        (which would make allocated ASNs read as unassigned).
        """
        if not hasattr(self, "_data_files"):
            self._data_files = []

            for rir in self.rir_lists:
                rir_file_path = os.path.join(
                    data_path,
                    f"delegated-{rir}-extended-latest",
                )
                self.download_data(rir, rir_file_path, cache_days)
                self._data_files.append(rir_file_path)

        if not hasattr(self, "_data"):
            self._data = {}

            for rir_file_path in self._data_files:
                logger.debug("loading RIR assignment data from %s", rir_file_path)
                # download_data guarantees each file is present and valid (or
                # raised), so parse directly here
                with open(rir_file_path) as fh:
                    text = fh.read()

                for line in text.splitlines():
                    asns = self.parse_data(line)

                    if not asns:
                        continue

                    try:
                        for data in asns:
                            self._data[int(data["asn"])] = data["status"]
                    except (TypeError, ValueError):
                        pass

        return self._data

    def _cache_expired(self, file_path, cache_days):
        """True if `file_path` is missing or older than `cache_days`. Uses
        elapsed seconds; the old `.days > cache_days` floored to whole days, so
        `cache_days=1` only refreshed at ~48h instead of 24h.
        """
        if not os.path.exists(file_path):
            return True
        age = datetime.datetime.now() - datetime.datetime.fromtimestamp(
            os.path.getmtime(file_path)
        )
        return age.total_seconds() > cache_days * 86400

    def _file_valid(self, rir, file_path):
        """True if `file_path` exists and passes content validation."""
        if not os.path.exists(file_path):
            return False
        try:
            with open(file_path) as fh:
                self.validate_content(rir, fh.read())
        except (OSError, RIRAssignmentError):
            return False
        return True

    def download_data(self, rir, file_path, cache_days=1):
        """Download RIR network assignment status data from RIPE
        https://ftp.ripe.net/pub/stats/{rir}/delegated-{rir}-extended-latest

        The body is checked (HTTP status + completeness) and written atomically.
        A stale or corrupt cache is re-downloaded; a failed/truncated fetch never
        clobbers a valid cache (kept if present, else `RIRAssignmentError`).
        """
        # reuse a still-fresh cache only if it is actually valid; a stale or
        # corrupt cache falls through and is re-downloaded
        if not self._cache_expired(file_path, cache_days) and self._file_valid(
            rir, file_path
        ):
            return

        url = f"https://ftp.ripe.net/pub/stats/{rir}/delegated-{rir}-extended-latest"

        try:
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            text = response.text
            self.validate_content(rir, text)
        except (requests.RequestException, RIRAssignmentError) as exc:
            # fall back to a valid cache rather than clobber it with a bad fetch
            if self._file_valid(rir, file_path):
                logger.warning(
                    "RIR data fetch for %s failed (%s); keeping cached copy",
                    rir,
                    exc,
                )
                return
            raise RIRAssignmentError(
                f"could not fetch valid RIR data for {rir} and no usable cache exists: {exc}"
            ) from exc

        # write to a pid-unique temp file and atomically replace: concurrent
        # runs can't interleave, an interrupted write can't leave a partial
        # cache, and the temp file is cleaned up if the replace never happened
        tmp_path = f"{file_path}.{os.getpid()}.tmp"
        try:
            with open(tmp_path, "w") as file:
                file.write(text)
            os.replace(tmp_path, file_path)
        finally:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)

    def get_status(self, asn):
        """Get RIR assignment status for an ASN"""
        if not hasattr(self, "_data"):
            self.load_data()

        return self._data.get(asn)
