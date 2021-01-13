import argparse
import sys

import munge
import munge.click

import rdap
from rdap.config import Config


def add_options(parser, options):
    for opt in options:
        name = opt.pop("name")

        # clicks is_flag
        if "is_flag" in opt:
            del opt["is_flag"]
            opt["action"] = "store_true"

        parser.add_argument(name, **opt)


class Context(munge.click.Context):
    """
    command line interface context
    """

    app_name = "rdap"
    config_class = Config


def main(argv=None):
    if argv is None:
        argv = sys.argv[1:]

    ctx = Context()

    parser = argparse.ArgumentParser(description="rdap")
    add_options(parser, Context.option_list())
    parser.add_argument(
        "--version",
        action="version",
        version="{}s version {}".format("%(prog)", rdap.__version__),
    )
    parser.add_argument("--output-format", help="output format (yaml, json, text)")
    parser.add_argument(
        "--show-requests", action="store_true", help="show all requests"
    )
    parser.add_argument(
        "--parse", action="store_true", help="parse data into object before display"
    )
    parser.add_argument(
        "--write-bootstrap-data",
        action="store_true",
        help="write bootstrap data for type (as query)",
    )

    parser.add_argument("query", nargs="+")
    args = parser.parse_args(argv)

    # get dict of options and update config
    argd = vars(args)
    ctx.update_options(argd)

    client = rdap.RdapClient(ctx.config)
    output_format = argd.get("output_format")
    if not output_format:
        output_format = ctx.config.get_nested("rdap", "output_format")

    if argd.get("write_bootstrap_data"):
        for each in argd["query"]:
            client.write_bootstrap_data(each)
        return 0

    codec = munge.get_codec(output_format)()
    for each in argd["query"]:
        obj = client.get(each)
        if argd.get("parse", False):
            print(codec.dumps(obj.parsed()))
        else:
            print(codec.dumps(obj.data))

    if argd.get("show_requests", False):
        print("# Requests")
        for each in client.history:
            print("{} {}".format(*each))

    return 0


if __name__ == "__main__":
    main()
