# Diagnose before changing anything

These are guided exercises, not claims of personal completion. Use only your lab process. Do not stop unrelated services or alter your laptop's firewall.

## 1. A stopped service

**Business impact:** a monitoring endpoint is unavailable. Establish whether there is a listener before investigating application data.

1. Confirm `curl -i --max-time 3 http://127.0.0.1:8088/health` returns 200.
2. Stop the service in terminal A with Ctrl+C.
3. Repeat curl. Inspect `ss -ltnp 'sport = :8088'`.
4. Record the connection error and missing listener. A connection failure alone does not prove the process stopped; the listener observation supports that diagnosis.
5. Restart `python3 scripts/service.py --port 8088`. Repeat curl and ss.

**Recovery evidence:** a listener and HTTP 200. **Prevention discussion:** a supervisor and health checks could restart/detect failed processes; this lab does not implement systemd.

## 2. Wrong client port

**Business impact:** a healthy application appears down because a caller has incorrect configuration.

1. Keep the service running on 8088. Verify no listener on 8089 using `ss -ltn 'sport = :8089'`. If occupied, pick another unused high port and substitute it below.
2. Run `curl -i --max-time 3 http://127.0.0.1:8089/health`.
3. Compare with the announced service port, `ss -ltnp 'sport = :8088'`, and the successful curl to 8088.
4. Correct the client URL to port 8088; do not restart the healthy server.

**Evidence:** wrong-port failure and correct-port success at the same time. This is loopback TCP configuration troubleshooting, not a multi-host network or firewall exercise. Automated tests reserve a non-listening port to avoid probing arbitrary occupied ports.

## 3. Wrong route

1. Request `curl -i http://127.0.0.1:8088/missing`.
2. Observe HTTP 404 and the service access log in terminal A.
3. Request `/health` and verify 200.

An HTTP response proves an HTTP server responded. Restarting network interfaces would not fix the route mismatch. Prevention: document endpoint paths and test caller configuration.

## 4. A reachable but unhealthy application

1. From the project directory run `mkdir -p runtime` then `touch runtime/dependency.failed`.
2. Request `/health`; observe 503 and `simulated_dependency_failure` in the JSON response.
3. Check `ss` to confirm a listener remains. Run the health monitor and verify it records an unhealthy service despite collecting host metrics.
4. Run `rm runtime/dependency.failed` (only the marker you created), then verify HTTP 200.

The marker intentionally simulates an unavailable dependency. There is no real database dependency behind this service. Prevention discussion: dependency-specific checks, retry limits and runbooks.

## Stretch exercise: a real two-VM network lab

Not implemented or tested in this package. When ready, create two disposable VMs on an isolated network. Record addresses/routes, verify connectivity, introduce one VM-specific configuration fault, then diagnose and restore it. Capture evidence from both ends. Do not claim this exercise until you perform it.
