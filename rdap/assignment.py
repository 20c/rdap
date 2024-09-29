import datetime
import os

import requests


class RIRAssignmentLookup:
    """Fetch RIR assignement status lists from ripe and lookup
    assignment per asn

    Files will be downloaded from  https://ftp.ripe.net/pub/stats/{rir}/delegated-{rir}-extended-latest
    """

    rir_lists = ["afrinic", "apnic", "arin", "lacnic", "ripencc"]

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
            asns = None

            asns = [{"asn": int(asn) + i, "status": status} for i in range(count)]

            return asns

        except IndexError:
            return None

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
                print(rir_file_path)
                with open(rir_file_path) as fh:
                    for line in fh.read().splitlines():
                        asns = self.parse_data(line)

                        if not asns:
                            continue

                        try:
                            for data in asns:
                                self._data[int(data["asn"])] = data["status"]
                        except (TypeError, ValueError):
                            pass

        return self._data

    def download_data(self, rir, file_path, cache_days=1):
        """Download RIR network assignment status data from RIPE
        https://ftp.ripe.net/pub/stats/{rir}/delegated-{rir}-extended-latesy
        """
        # Only download/re-download the file if it doesn't exist or the file is older than a day django_settings.RIR_ALLOCATION_DATA_CACHE_DAYS
        if (
            not os.path.exists(file_path)
            or (
                datetime.datetime.now()
                - datetime.datetime.fromtimestamp(os.path.getmtime(file_path))
            ).days
            > cache_days
        ):
            url = (
                f"https://ftp.ripe.net/pub/stats/{rir}/delegated-{rir}-extended-latest"
            )
            response = requests.get(url)

            with open(file_path, "w") as file:
                file.write(response.text)

    def get_status(self, asn):
        """Get RIR assignment status for an ASN"""
        if not hasattr(self, "_data"):
            self.load_data()

        return self._data.get(asn)
