
# rdap change log

## [Unreleased]
### Added
### Fixed
### Changed
### Deprecated
### Removed
### Security


## [0.5.0] 2019-12-18
### Added
- add config for request timeout, default to 0.5 seconds

### Changed
- bump pytest-filedata to 0.4.0 for pytest4


## [0.4.0] 2018-11-25
### Added
- add --parse option to display the parsed output
- RdapObject::handle
- ip address lookup
- domain name lookup

### Changed
- default CLI to display full data
- rename `raw` to `data` on RdapObjects


## [0.2.1] 2018-10-09
### Fixed
- long_description content type


## [0.2.0] 2018-10-09
### Added
- moved recurse_roles to config
- added support for LACNIC apikeys

### Changed
- RdapNotFoundError now inherits from RdapHTTPError instead of LookupError
- updated User-Agent
- converted to requests.Session()
