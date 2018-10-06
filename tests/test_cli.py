import pytest

from rdap.__main__ import main


def test_usage():
    with pytest.raises(SystemExit) as excinfo:
        main()
    assert 2 == excinfo.value.code


def test_lookup():
    args = ["as63311", "--show-requests"]
    main(args)
