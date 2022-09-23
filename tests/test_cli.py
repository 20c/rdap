import os

import pytest

from rdap.cli import main


def test_usage():
    with pytest.raises(SystemExit) as excinfo:
        main()
    assert 2 == excinfo.value.code


def test_lookup():
    args = ["as63311", "--show-requests"]
    rv = main(args)
    assert rv == 0


def test_write_bootstrap_data(tmpdir):
    config_file = str(os.path.join(tmpdir, "config.yml"))
    with open(config_file, "w") as fh:
        fh.write("rdap: {}")

    args = ["--home", str(tmpdir), "--write-bootstrap-data", "asn"]
    rv = main(args)
    assert os.path.isfile(os.path.join(tmpdir, "bootstrap", "asn.json"))
    assert rv == 0
