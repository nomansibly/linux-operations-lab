# Validation provenance

Executed in the assistant Linux workspace, not the user laptop.

- Four real loopback failure/recovery scenarios: passed.
- Four metric regression tests: passed.
- Monitor without service: three samples, three unhealthy readings.
- Monitor with running service on an allocated loopback port: three samples, all HTTP 200.
- SQLite read-only summary: executed successfully.

Host resource numbers are properties of this execution environment and may be virtualized. GitHub-hosted CI, WSL setup and user-performed manual commands have not been validated here.
