"""Run genuine local failure/recovery checks; save machine-readable evidence."""
import argparse
import json
import socket
import subprocess
import sys
import tempfile
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OPENER = urllib.request.build_opener(urllib.request.ProxyHandler({}))

def probe(port, path='/health'):
    try:
        with OPENER.open(f'http://127.0.0.1:{port}{path}', timeout=2) as r:
            return {'status': r.status, 'body': r.read().decode()}
    except urllib.error.HTTPError as e:
        return {'status': e.code, 'body': e.read().decode()}
    except (urllib.error.URLError, TimeoutError, ConnectionError) as e:
        return {'status': None, 'error': str(e)}

def main(output):
    output.mkdir(parents=True, exist_ok=True)
    cases = []
    with tempfile.TemporaryDirectory(prefix='linux-lab-') as folder:
        fault = Path(folder)/'dependency.failed'
        log = open(output/'service.log', 'w')
        proc = None
        def start():
            child = subprocess.Popen([sys.executable, str(ROOT/'scripts/service.py'), '--port', '0', '--fault-file', str(fault)], stdout=subprocess.PIPE, stderr=log, text=True)
            # Startup readiness is confirmed by the child announcing its bound port.
            import selectors
            with selectors.DefaultSelector() as sel:
                sel.register(child.stdout, selectors.EVENT_READ)
                if not sel.select(10):
                    child.terminate(); child.wait(timeout=5)
                    raise RuntimeError('Service startup timed out')
            line = child.stdout.readline()
            if not line:
                child.wait(timeout=5)
                raise RuntimeError('Service failed; inspect service.log')
            return child, json.loads(line)['port']
        def stop(child):
            child.terminate()
            try: child.wait(timeout=5)
            except subprocess.TimeoutExpired: child.kill(); child.wait()
            child.stdout.close()
        def record(name, symptom, recovered, expected, diagnosis):
            passed = symptom['status'] == expected and recovered['status'] == 200
            cases.append({'scenario': name, 'symptom': symptom, 'after_fix': recovered, 'passed': passed, 'diagnosis': diagnosis})
            if not passed: raise AssertionError(f'{name}: unexpected result')
        try:
            proc, port = start()
            assert probe(port)['status'] == 200
            stop(proc); proc = None
            symptom = probe(port)
            proc, port = start()
            record('service_stopped', symptom, probe(port), None, 'Listener process stopped; restart managed lab process and use its announced port.')
            # Reserve a different port without listening: do not scan arbitrary ports.
            with socket.socket() as reservation:
                reservation.bind(('127.0.0.1',0))
                symptom = probe(reservation.getsockname()[1])
            record('wrong_client_port', symptom, probe(port), None, 'Healthy server; client targeted a non-listening port. Correct client configuration.')
            symptom = probe(port, '/missing')
            record('wrong_http_route', symptom, probe(port), 404, 'TCP and HTTP work; correct URL path instead of restarting networking.')
            fault.touch()
            symptom = probe(port)
            fault.unlink()
            record('dependency_unavailable', symptom, probe(port), 503, 'Application is reachable but explicitly simulates dependency failure; remove only lab marker.')
        finally:
            if proc is not None: stop(proc)
            log.close()
            (output/'scenarios.json').write_text(json.dumps({'generated_at':datetime.now(timezone.utc).isoformat(), 'environment':'automated local loopback lab; not physical data center equipment', 'cases':cases},indent=2)+'\n')
    print(f'{len(cases)} scenarios passed; evidence: {output}')

if __name__ == '__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--output',type=Path,default=ROOT/'runtime/evidence')
    main(p.parse_args().output)
