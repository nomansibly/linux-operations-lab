"""One-command integration validation, evidence capture and showcase generation."""
import argparse
import csv
import json
import platform
import selectors
import socket
import sqlite3
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]

def execute(command, output):
    result=subprocess.run(command,cwd=ROOT,text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,timeout=60)
    output.write_text(result.stdout)
    if result.returncode: raise RuntimeError(f'Check failed: {output}')

def main(out,site):
    out.mkdir(parents=True,exist_ok=True)
    if (out/'validation.json').exists():
        raise ValueError('Choose a fresh --output directory to preserve earlier evidence.')
    execute([sys.executable,'-m','unittest','discover','-s','tests','-v'],out/'unit-tests.txt')
    execute([sys.executable,'scripts/run_scenarios.py','--output',str(out/'scenarios')],out/'scenarios-run.txt')
    def monitor(port,name):
        target=out/name
        execute([sys.executable,'scripts/health_monitor.py','--port',str(port),'--samples','5','--interval','0.2','--output',str(target)],out/f'{name}-run.txt')
        with sqlite3.connect(target/'health.sqlite') as conn:
            rows=conn.execute('SELECT http_status, alerts FROM samples').fetchall()
        if len(rows)!=5: raise AssertionError('Expected five persistent samples')
        csvrows=list(csv.DictReader((target/'health.csv').open()))
        if len(csvrows)!=5: raise AssertionError('CSV mismatch')
        execute([sys.executable,'scripts/query_health.py',str(target/'health.sqlite')],out/f'{name}-sql.txt')
        return rows
    with socket.socket() as reserved:
        reserved.bind(('127.0.0.1',0))
        rows=monitor(reserved.getsockname()[1],'unhealthy')
        assert all(status is None and 'service_unhealthy' in json.loads(alert) for status,alert in rows)
    with (out/'healthy-service.log').open('w') as log:
        proc=subprocess.Popen([sys.executable,str(ROOT/'scripts/service.py'),'--port','0','--fault-file',str(out/'unused-fault-marker')],stdout=subprocess.PIPE,stderr=log,text=True)
        try:
            with selectors.DefaultSelector() as selector:
                selector.register(proc.stdout,selectors.EVENT_READ)
                if not selector.select(10): raise RuntimeError('Service readiness timeout')
            port=json.loads(proc.stdout.readline())['port']
            rows=monitor(port,'healthy')
            assert all(status==200 and 'service_unhealthy' not in json.loads(alert) for status,alert in rows)
        finally:
            proc.terminate()
            try: proc.wait(timeout=5)
            except subprocess.TimeoutExpired: proc.kill();proc.wait()
            proc.stdout.close()
    report={'generated_at':datetime.now(timezone.utc).isoformat(),'environment':'assistant execution environment' if out.name=='completed' else 'local execution environment','python':platform.python_version(),'platform':platform.system(),'scenario_checks':4,'unit_tests':4,'healthy_samples':5,'unhealthy_samples':5,'status':'passed','limitations':['Loopback network only; no two-VM, DNS or physical hardware validation.','GitHub-hosted deployment status is not established by a local run.']}
    (out/'validation.json').write_text(json.dumps(report,indent=2)+'\n')
    from build_showcase import build
    build(out,site)
    print(f'All checks passed. Evidence: {out}. Showcase: {site}')

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--output',type=Path,default=ROOT/'runtime'/datetime.now(timezone.utc).strftime('demo-%Y%m%d-%H%M%S'))
    p.add_argument('--site',type=Path,default=ROOT/'docs/index.html')
    a=p.parse_args();main(a.output.resolve(),a.site.resolve())
