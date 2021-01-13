import munge


class Config(munge.Config):
    """
    command line interface config
    """

    defaults = {
        "config": {
            "rdap": {
                "bootstrap_url": "https://rdap.org/",
                "self_bootstrap": False,
                "bootstrap_data_url": "https://data.iana.org/rdap/",
                # bootstrap dir, defaults to config_dir/bootstrap
                "bootstrap_dir": None,
                "bootstrap_cache_ttl": 25,
                "output_format": "yaml",
                "ignore_recurse_errors": False,
                "recurse_roles": ["administrative", "technical"],
                "lacnic_apikey": None,
                "timeout": 5,
            },
        },
        "codec": "yaml",
    }
