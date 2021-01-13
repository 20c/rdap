
# rdap

[![PyPI](https://img.shields.io/pypi/v/rdap.svg?maxAge=3600)](https://pypi.python.org/pypi/rdap)
[![PyPI](https://img.shields.io/pypi/pyversions/rdap.svg?maxAge=3600)](https://pypi.python.org/pypi/rdap)
[![Tests](https://github.com/20c/rdap/workflows/tests/badge.svg)](https://github.com/20c/rdap)
[![Codecov](https://img.shields.io/codecov/c/github/20c/rdap/master.svg?maxAge=3600)](https://codecov.io/github/20c/rdap)

Registration Data Access Protocol tools

## Installation

```sh
pip install rdap
```


## Usage

```sh
usage: rdap [-h] [--debug] [--home HOME] [--verbose] [--quiet] [--version] [--output-format OUTPUT_FORMAT] [--show-requests] [--parse]
            [--write-bootstrap-data]
            query [query ...]

rdap

positional arguments:
  query

optional arguments:
  -h, --help            show this help message and exit
  --debug               enable extra debug output
  --home HOME           specify the home directory, by default will check in order: $RDAP_HOME, ./.rdap, /home/$USER/.rdap,
                        /home/$USER/.config/rdap
  --verbose             enable more verbose output
  --quiet               no output at all
  --version             show version number and exit
  --output-format OUTPUT_FORMAT
                        output format (yaml, json, text)
  --show-requests       show all requests
  --parse               parse data into object before display
  --write-bootstrap-data
                        write bootstrap data for type (as query)
```


## Config file

The client uses the `--home` option to point to a directory, by default will check in order: `$RDAP_HOME`, `./.rdap`, `~/.rdap`, `~/.config/rdap`

The directory should have a `config.yaml` file in it, defaults shown below.

```yaml
rdap:
  # URL to bootstrap the initial request off
  bootstrap_url: https://rdap.db.ripe.net/
  # boolean to use data from bootstrap_data_url instead of a bootstrap server
  self_bootstrap: False
  # url to load bootstrap data from
  bootstrap_data_url: "https://data.iana.org/rdap/"
  # length of time in hours to keep bootstrap data
  bootstrap_cache_ttl: 25
  # how to format the output
  output_format: yaml
  # API key for use at rdap.lacnic.net
  lacnic_apikey: None
  # role types to recursively query when processing
  recurse_roles: ["administrative", "technical"]
  # HTTP request timeout in seconds, used for both connect and read
  timeout: 0.5
```


### License

Copyright 2016 20C, LLC

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this softare except in compliance with the License.
You may obtain a copy of the License at

   http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
