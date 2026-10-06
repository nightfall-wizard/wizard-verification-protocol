
# WVP Versioning Policy

WVP evidence packs use explicit version labels.

## Evidence version

For Nightfall v1.0.5, WVP evidence is stored under:

`reports/nightfall/v1.0.5`

## Versioned release pack

Release packs are stored under:

`release-packs/nightfall/v1.0.5`

## Version update rule

Create a new version directory when:

- the upstream project version changes
- evidence scope materially changes
- release-pack contents materially change
- public report structure changes
- checker behavior materially changes

## Allowed versioned artifacts

- JSON reports
- Markdown reports
- release-pack manifest
- release-pack checksum
- safe templates
- safe toy inputs
- unit tests
- WVP checkers

## Boundary

Versioning tracks WVP evidence state. It does not certify project safety.
