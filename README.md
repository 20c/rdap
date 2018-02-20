
# rdap

[![PyPI](https://img.shields.io/pypi/v/rdap.svg?maxAge=3600)](https://pypi.python.org/pypi/rdap)
[![PyPI](https://img.shields.io/pypi/pyversions/rdap.svg?maxAge=3600)](https://pypi.python.org/pypi/rdap)
[![Travis CI](https://img.shields.io/travis/20c/rdap.svg?maxAge=3600)](https://travis-ci.org/20c/rdap)
[![Code Health](https://landscape.io/github/20c/rdap/master/landscape.svg?style=flat)](https://landscape.io/github/20c/rdap/master)
[![Codecov](https://img.shields.io/codecov/c/github/20c/rdap/master.svg?maxAge=3600)](https://codecov.io/github/20c/rdap)
[![Requires.io](https://img.shields.io/requires/github/20c/rdap.svg?maxAge=3600)](https://requires.io/github/20c/rdap/requirements)

Registration Data Access Protocol tools

### Usage

```sh
usage: rdap [-h] [--debug] [--home HOME] [--verbose] [--quiet] [--version]
            [--output-format OUTPUT_FORMAT] [--show-requests]
            query [query ...]

rdap

positional arguments:
  query

optional arguments:
  -h, --help            show this help message and exit
  --debug               enable extra debug output
  --home HOME           specify the home directory, by default will check in
                        order: $RDAP_HOME, ./.rdap, /home/grizz/.rdap,
                        /home/grizz/.config/rdap
  --verbose             enable more verbose output
  --quiet               no output at all
  --version             show program's version number and exit
  --output-format OUTPUT_FORMAT
                        output format (yaml, json, text)
  --show-requests       show all requests
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
