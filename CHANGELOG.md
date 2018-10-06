
# rdap change log

## [Unreleased]
### Added
- moved recurse_roles to config
- added support for LACNIC apikeys

### Fixed
### Changed
- RdapNotFoundError now inherits from RdapHTTPError instead of LookupError
- updated User-Agent
- converted to requests.Session()

### Deprecated
### Removed
### Security
