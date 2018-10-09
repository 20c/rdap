
# rdap change log

## [Unreleased]
### Added
### Fixed
### Changed
### Deprecated
### Removed
### Security


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
