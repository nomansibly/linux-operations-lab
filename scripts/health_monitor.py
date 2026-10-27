"""Linux host metrics + HTTP health -> SQLite + CSV; bounded sampling, no root."""
import argparse
import csv
import json
import shutil
import sqlite3
import time
from datetime import datetime, timezone
from pathlib import Path
from run_scenarios import probe

def cpu_ticks():
    values=list(map(int,Path('/proc/stat').read_text().splitlines()[0].split()[1:]))
    # guest times are already included in user/nice; exclude double counting.
    return sum(values[:8]),values[3]+values[4]

def cpu_percent(before,after):
    total=after[0]-before[0]
    return None if total<=0 else round(100*(1-(after[1]-before[1])/total),2)

def memory_percent():
    values={line.split(':')[0]:int(line.split()[1]) for line in Path('/proc/meminfo').read_text().splitlines()}
    return round(100*(1-values['MemAvailable']/values['MemTotal']),2)

def alerts(cpu,memory,disk,status):
    result=[]
    for name,value in [('cpu',cpu),('memory',memory),('disk',disk)]:
        if value is None: result.append(name+'_unknown')
        elif value>=85: result.append(name+'_high')
    if status!=200: result.append('service_unhealthy')
    return result

def main(a):
    if a.samples<1 or a.interval<=0: raise ValueError('samples >= 1 and interval > 0 required')
    a.output.mkdir(parents=True,exist_ok=True)
    with sqlite3.connect(a.output/'health.sqlite') as conn:
        conn.execute('CREATE TABLE IF NOT EXISTS samples (id INTEGER PRIMARY KEY, recorded_at TEXT NOT NULL, cpu_pct REAL, memory_pct REAL, disk_pct REAL, http_status INTEGER, alerts TEXT NOT NULL)')
        rows=[]
        for _ in range(a.samples):
            before=cpu_ticks(); time.sleep(a.interval); cpu=cpu_percent(before,cpu_ticks())
            memory=memory_percent(); disk=shutil.disk_usage(a.disk_path)
            disk_pct=round(100*disk.used/disk.total,2); status=probe(a.port)['status']
            row=(datetime.now(timezone.utc).isoformat(),cpu,memory,disk_pct,status,json.dumps(alerts(cpu,memory,disk_pct,status)))
            conn.execute('INSERT INTO samples(recorded_at,cpu_pct,memory_pct,disk_pct,http_status,alerts) VALUES (?,?,?,?,?,?)',row)
            conn.commit(); rows.append(row)
        with (a.output/'health.csv').open('w',newline='') as f:
            writer=csv.writer(f);writer.writerow(['recorded_at','cpu_pct','memory_pct','disk_pct','http_status','alerts']);writer.writerows(rows)
    # A dependency-free HTML report; missing values remain visibly unknown.
    import html
    body=''.join('<tr>'+''.join('<td>'+html.escape('unknown' if x is None else str(x))+'</td>' for x in row)+'</tr>' for row in rows)
    (a.output/'health.html').write_text('<!doctype html><meta charset="utf-8"><title>Linux lab health</title><style>body{font:16px system-ui;margin:40px;background:#f2f5f9;color:#18324a}td,th{padding:12px;border-bottom:1px solid #ccd}table{background:white;border-collapse:collapse}</style><h1>Linux Operations Lab — health samples</h1><p>Local lab observations. CPU: <i>/proc/stat</i> delta; memory: MemAvailable; disk: filesystem usage. These are not hardware sensor temperatures.</p><table><tr><th>UTC</th><th>CPU %</th><th>Memory %</th><th>Disk %</th><th>HTTP</th><th>Alerts</th></tr>'+body+'</table>')
    print(f'Saved {len(rows)} samples to {a.output}')

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--samples',type=int,default=5);p.add_argument('--interval',type=float,default=1)
    p.add_argument('--port',type=int,default=8088);p.add_argument('--disk-path',default='.')
    p.add_argument('--output',type=Path,default=Path('runtime/monitor'))
    main(p.parse_args())
