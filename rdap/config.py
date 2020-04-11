import munge


class Config(munge.Config):
    """
    command line interface config
    """

    defaults = {
        "config": {
            "rdap": {
                "bootstrap_url": "https://rdap.org/",
                "output_format": "yaml",
                "recurse_roles": ["administrative", "technical"],
                "lacnic_apikey": None,
                "timeout": 0.5,
            },
        },
        "codec": "yaml",
    }
