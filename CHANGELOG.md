# Changelog


## Unreleased
### Added
- black formatting
- more object types [#4]
### Changed
- default bootstrap_url to rdap.org
### Removed
- python 2.7 and 3.4 support


## 0.5.1
### Fixed
- changed MANIFEST file to not include tmp dirs, #3


## 0.5.0
### Added
- add config for request timeout, default to 0.5 seconds
### Changed
- bump pytest-filedata to 0.4.0 for pytest4


## 0.4.0
### Added
- add --parse option to display the parsed output
- RdapObject::handle
- ip address lookup
- domain name lookup
### Changed
- default CLI to display full data
- rename `raw` to `data` on RdapObjects


## 0.2.1
### Fixed
- long_description content type


## 0.2.0
### Added
- moved recurse_roles to config
- added support for LACNIC apikeys
### Changed
- RdapNotFoundError now inherits from RdapHTTPError instead of LookupError
- updated User-Agent
- converted to requests.Session()