import argparse
import json
import os
import sys

from rdap import RdapClient


def rdap_autnum_file_list(directory):
    input_file_list = []
    expected_file_list = []
    for filename in os.listdir(directory):
        if os.path.isfile(os.path.join(directory, filename)) and filename.endswith(
            ".input",
        ):
            input_file_list.append(filename)
        elif os.path.isfile(os.path.join(directory, filename)) and filename.endswith(
            ".expected",
        ):
            expected_file_list.append(filename)
    return input_file_list, expected_file_list


def update_autnum_entries(rdapc, file_name, filepath):
    asn = int(file_name.split(".")[0])
    rdap_data = rdapc.get_asn(asn)
    full_filepath = os.path.join(filepath, file_name)

    with open(full_filepath, "w") as output_file:
        if file_name.split(".")[-1] == "input":
            formatted_data = json.dumps(rdap_data.data, indent=2)
            output_file.write(str(formatted_data))
        else:
            formatted_parsed = json.dumps(rdap_data.parsed(), indent=2)
            output_file.write(str(formatted_parsed))

    print(f"RDAP data for ASN {asn} written to {full_filepath}")


def main(include_expected=False):
    path_autnum = "./tests/data/rdap/autnum/"
    input_file_list, expected_file_list = rdap_autnum_file_list(path_autnum)
    rdapc = RdapClient()
    for file in input_file_list:
        update_autnum_entries(rdapc, file, path_autnum)
    if include_expected:
        for file in expected_file_list:
            update_autnum_entries(rdapc, file, path_autnum)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Script Description")

    # Add the --include-expected option
    parser.add_argument(
        "--include-expected",
        action="store_true",
        help="Include expected",
    )

    args = parser.parse_args()

    # Call the main function with the value of --include-expected
    main(include_expected=args.include_expected)

    sys.exit()
