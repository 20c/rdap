
import munge


class Config(munge.Config):
    """
    command line interface config
    """
    defaults = {
        'config': {
            'rdap': {
                "bootstrap_url": "https://rdap.db.ripe.net/",
                "output_format": "yaml",
                },
            },
        'codec': 'yaml',
        }
