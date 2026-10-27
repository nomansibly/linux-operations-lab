# Linux Operations Lab

**Service recovery · TCP/HTTP diagnostics · Host monitoring · SQL evidence**

A reproducible, local-only portfolio lab prepared for Sibly Noman. Four controlled failures teach how to separate process, client configuration, HTTP routing and application dependency problems. A Python monitor records Linux metrics and service health in SQLite for SQL analysis.

> Evidence shipped here was generated in the assistant's Linux execution environment. It is not evidence of the owner's laptop work, physical server maintenance, or production operations. Run the exercises yourself and add your own observations before claiming hands-on completion.

## Verified demonstration

| Scenario | Observed symptom | Recovery | Result |
|---|---|---|---|
| Service stopped | Connection failure | Restart the lab process | HTTP 200 |
| Wrong client port | Connection failure | Use actual listener port | HTTP 200 |
| Wrong HTTP route | HTTP 404 | Use `/health` | HTTP 200 |
| Simulated dependency unavailable | HTTP 503 | Remove lab fault marker | HTTP 200 |

[Actual scenario evidence](evidence/automated/scenarios.json) · [HTTP access log](evidence/automated/service.log) · [Health samples](evidence/monitor/health.csv) · [Health report HTML](evidence/monitor/health.html)

Four scenarios and four metric tests passed in the assistant environment. The full integration run additionally validated ten persisted samples and read-only SQL summaries. The health monitor was checked with an absent service (unhealthy status preserved), and with a running service (HTTP 200). GitHub Actions is provided but its hosted run remains unverified until you publish.

## Complete automated demonstration

```bash
python3 scripts/complete_demo.py
```

This single command performs all tests, runs every scenario, collects and verifies five healthy and five unhealthy samples in SQLite/CSV, executes SQL summaries and regenerates `docs/index.html`. No manual failure injection is required. Each run gets a fresh timestamped output folder in `runtime/`. The checked-in [completed evidence](evidence/completed/validation.json) records an actual successful run here.

**Showcase:** open `docs/index.html` in any browser; it is self-contained and works offline. A GitHub Pages deployment workflow is included. Once repository access is connected, publishing requires setting Pages source to GitHub Actions and running **Publish showcase**. No public deployment is claimed yet.

## Start here — Linux or Ubuntu in Windows WSL

Requires Linux, Python 3.10+ and its standard library. No pip install, Docker, cloud account, or root permission is required for the automated lab. Linux `/proc` is required for the monitor. Windows users should run these commands inside Ubuntu/WSL, not ordinary PowerShell. See [Windows setup](docs/WINDOWS.md).

Open a terminal in this extracted repository folder:

```bash
python3 -m unittest discover -s tests -v
python3 scripts/run_scenarios.py
python3 scripts/health_monitor.py --samples 5 --interval 1
```

The scenario runner starts its own loopback-only service, induces four failures, checks recovery, and cleans up its own process. It does not change system networking or services. Files go to `runtime/` so your new output does not overwrite the bundled evidence. The service is stopped when the scenario runner finishes: an immediate monitor run should report `service_unhealthy`.

## Optional manual troubleshooting practice

In **terminal A**, start the service and leave it running:

```bash
python3 scripts/service.py --port 8088
```

In **terminal B**, capture a baseline:

```bash
curl -i --max-time 3 http://127.0.0.1:8088/health
ss -ltnp 'sport = :8088'
python3 scripts/health_monitor.py --port 8088 --samples 5
```

Now follow [the four case studies](docs/CASE_STUDIES.md), one at a time. Collect your commands and actual output using [the evidence template](docs/MY_LAB_TEMPLATE.md). Open `runtime/monitor/health.html` in a browser to review the monitor table. Stop the service with Ctrl+C in terminal A.

## SQL analysis of collected health data

SQLite makes this exercise easy to run without a separate database. It complements the PostgreSQL DCIM project; it is not a PostgreSQL integration. Use Python's built-in SQLite client:

```bash
python3 scripts/query_health.py runtime/monitor/health.sqlite
```

The SQLite database appends samples between runs. CSV and HTML contain only the latest invocation. Remove only your local `runtime/monitor/health.sqlite` if you intentionally want a fresh dataset.

## Portfolio publication

1. Create a public GitHub repository named `linux-operations-lab`.
2. Upload the contents of this folder, including `.github/workflows/checks.yml`.
3. Open Actions and verify the **Linux lab checks** workflow is green.
4. Optional: complete the manual cases on your machine and add personal evidence in `evidence/my-laptop/`.
5. For optional manual practice, use the case-study template to explain observations.
6. Pin this repository alongside your PostgreSQL DCIM project.

No website is required. An optional two-minute screen recording should show a failure, a diagnostic observation, the fix and successful verification.

## Skills and scope

Shows Python process management, HTTP status interpretation, loopback TCP diagnostics, Linux host metrics, SQLite queries, reproducible tests and incident documentation. It does **not** demonstrate physical hardware replacement, switch configuration, two-VM routing, actual DNS repair, systemd administration, or production on-call experience.

See [metric definitions and limitations](docs/METRICS.md) and [interview practice](docs/INTERVIEW.md). MIT license.
