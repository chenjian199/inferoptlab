"""Periodically download progress and verified metrics; retry VPN outages.

This observer never launches, stops, or changes a serving container. A failed
scan is recorded as needs_attention, not silently retried or declared complete.
"""
import argparse
from collections import Counter
from datetime import datetime, timezone
import json
from pathlib import Path
import subprocess
import sys
import time


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--attempt', default='r3')
    parser.add_argument('--interval', type=int, default=60)
    parser.add_argument('--once', action='store_true')
    args = parser.parse_args()
    if not args.attempt.isalnum() or args.interval < 10:
        raise SystemExit('invalid attempt or interval')
    root = Path(__file__).resolve().parent
    receipt = root/('monitor-'+args.attempt+'.json')
    last_collected = -1
    failures = 0
    while True:
        started = time.monotonic()
        now = datetime.now(timezone.utc).isoformat()
        result = subprocess.run([sys.executable, str(root/'poll_scan.py'), '--attempt',
                                 args.attempt, '--compact'], capture_output=True, text=True,
                                encoding='utf-8', errors='replace', timeout=50)
        status = {'checked_at': now, 'attempt': args.attempt}
        terminal = False
        if result.returncode:
            failures += 1
            status.update(status='observation_unavailable', consecutive_errors=failures,
                          error=(result.stderr or result.stdout)[-2000:])
        else:
            failures = 0
            data = json.loads((root/'scan-status.json').read_text(encoding='utf-8'))
            state = data['state']
            counts = dict(Counter(p['status'] for p in state.get('points', [])))
            terminal = state['status'] in {'completed', 'finished_with_exclusions', 'failed'}
            controller = data['controller']
            if isinstance(controller, dict) and not controller.get('Running'):
                terminal = True
            status.update(status='needs_attention' if terminal and state['status'] not in
                          {'completed', 'finished_with_exclusions'} else state['status'],
                          counts=counts, group=state.get('group'), point=state.get('point'))
            completed = counts.get('completed', 0)
            if terminal or completed >= last_collected+6:
                fetched = subprocess.run([sys.executable, str(root/'collect_scan.py'),
                                          '--attempt', args.attempt], capture_output=True,
                                         text=True, encoding='utf-8', errors='replace', timeout=150)
                status['download'] = {'ok': fetched.returncode == 0,
                                      'message': (fetched.stdout+fetched.stderr)[-2000:]}
                if fetched.returncode == 0:
                    last_collected = completed
                elif terminal:
                    terminal = False  # Retry the final download after a VPN outage.
        temp = receipt.with_suffix('.tmp')
        temp.write_text(json.dumps(status, indent=2, ensure_ascii=False), encoding='utf-8')
        temp.replace(receipt)
        print(json.dumps(status, ensure_ascii=False), flush=True)
        if args.once or terminal:
            return 1 if status['status'] == 'needs_attention' else 0
        time.sleep(max(1, args.interval-(time.monotonic()-started)))


if __name__ == '__main__':
    raise SystemExit(main())
