# WVP Release Pack Method

WVP-SEC-010 creates a versioned evidence bundle.

The release pack includes:

- WVP documentation
- Nightfall report artifacts
- JSON evidence files
- Markdown evidence files
- safe negative vectors
- fuzzing scaffold
- security templates
- executable WVP checkers
- unit tests
- CI workflow references
- bundle manifest
- archive checksum

The release pack is deterministic at the archive metadata level:

- sorted file list
- normalized tar metadata
- normalized gzip mtime
- SHA-256 checksum

A PASS means:

- a manifest exists
- a bundle archive exists
- archive checksum exists
- all manifest files exist
- safety boundary is explicit

A PASS does not mean:

- Nightfall is safe
- Nightfall is audited
- binaries are reproducible
- cryptography is correct
- consensus correctness is proven
