# What the monitor actually measures

- CPU: utilization over the sampling interval from `/proc/stat` tick deltas. Idle includes iowait. Guest ticks are excluded from the total because user/nice already include them. Zero elapsed ticks are unknown, not zero utilization.
- Memory: `(1 - MemAvailable / MemTotal) * 100` from `/proc/meminfo`.
- Disk: used filesystem bytes / total bytes for `--disk-path`, not disk I/O or device reliability.
- Service: one HTTP request to the chosen loopback port and `/health`; 200 means healthy in this lab. Non-200 and connection failures are unhealthy. This is not systemd status.
- Alerts: >=85% for each resource is illustrative policy. No email or external alerts are sent. Alerts are stored locally.

Container/WSL `/proc` values can reflect the host or VM rather than process/container limits. These samples must not be presented as physical server telemetry or a benchmark. No temperature or power sensor data is collected.

SQLite writes one row per completed sample. CSV/HTML represent the latest invocation, while SQLite retains earlier samples. Timestamps are UTC collection times; there is no production availability/SLA calculation. Sampling blocks for the chosen interval and HTTP probing adds latency. This is a bounded educational script, not a daemon.

A production collector would need resource-aware metrics, timeouts, authentication/TLS, external configuration, retention, batch writes, supervision and central storage. A future PostgreSQL adapter should use a separate host-metrics table: CPU utilization is not server power draw. No production scaling claim is made here.
