"""Read-only SQL summary of recorded lab metrics."""
import sqlite3
import sys
from pathlib import Path
p=Path(sys.argv[1] if len(sys.argv)>1 else 'runtime/monitor/health.sqlite').resolve()
with sqlite3.connect(p.as_uri()+'?mode=ro',uri=True) as conn:
    cur=conn.execute('''SELECT COUNT(*) AS samples,
      ROUND(AVG(cpu_pct),2) AS avg_cpu_pct,
      ROUND(MAX(memory_pct),2) AS peak_memory_pct,
      ROUND(MAX(disk_pct),2) AS peak_disk_pct,
      SUM(CASE WHEN http_status=200 THEN 0 ELSE 1 END) AS unhealthy_samples
      FROM samples''')
    print(dict(zip([c[0] for c in cur.description],cur.fetchone())))
