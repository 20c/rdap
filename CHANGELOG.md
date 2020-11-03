# Changelog


## Unreleased


## 1.1.0
### Added
- python 3.9
### Fixed
- ignore not found on nested handle lookups
### Changed
- improved exception message for unallocated ASNs
### Removed
- python 3.5


## 1.0.1
### Fixed
- better range check for unallocated ASNs


## 1.0.0
### Added
- black formatting
- more object types (#4)
- python 3.8 tests
### Fixed
- sort lists for consistent tests (#7)
### Changed
- default bootstrap_url to rdap.org
### Removed
- python 2.7 support
- python 3.4 tests


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