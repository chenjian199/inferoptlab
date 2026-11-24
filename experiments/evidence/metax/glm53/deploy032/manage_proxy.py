"""Manage only the task's loopback Mihomo process. Never print subscriptions."""
import argparse
import getpass
import json
import os
from pathlib import Path
import re
import secrets
import signal
import socket
import subprocess
import time
import urllib.parse
import urllib.request

ROOT = Path('/home/metax/glm53-vllm032/proxy')
CONFIG = ROOT / 'config.json'
PID = ROOT / 'mihomo.pid'
BINARY = ROOT / 'mihomo'


def save_private(path, value):
    temp = path.with_suffix(path.suffix + '.tmp')
    fd = os.open(temp, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
    with os.fdopen(fd, 'w') as f:
        f.write(value)
    temp.chmod(0o600)
    temp.replace(path)


def managed_pid():
    if not PID.exists():
        return None
    pid = int(PID.read_text())
    try:
        if Path(f'/proc/{pid}/exe').resolve(strict=True) == BINARY.resolve():
            return pid
    except FileNotFoundError:
        return None
    raise RuntimeError('PID does not belong to this task; refusing to signal it')


def api(path):
    cfg = json.loads(CONFIG.read_text())
    req = urllib.request.Request('http://127.0.0.1:19090' + path,
        headers={'Authorization': 'Bearer ' + cfg['secret']})
    op = urllib.request.build_opener(urllib.request.ProxyHandler({}))
    with op.open(req, timeout=5) as response:
        return json.load(response)


def stop():
    pid = managed_pid()
    if pid:
        os.kill(pid, signal.SIGTERM)
        for _ in range(50):
            if not managed_pid():
                return
            time.sleep(0.1)
        raise RuntimeError('Task proxy has not exited; no forced kill performed')


def start():
    if managed_pid():
        print('Task proxy is already running.')
        return
    for port in (17890, 19090):
        with socket.socket() as s:
            s.bind(('127.0.0.1', port))
    env = {k: v for k, v in os.environ.items() if k.lower() not in
           ('http_proxy', 'https_proxy', 'all_proxy')}
    check = subprocess.run([str(BINARY), '-t', '-d', str(ROOT), '-f', str(CONFIG)],
                           env=env, capture_output=True, text=True, timeout=90)
    if check.returncode:
        # Exclude URLs (which may contain credentials) from diagnostics.
        error = re.sub(r'https?://\S+', '<url-redacted>', check.stderr + check.stdout)
        save_private(ROOT / 'validation_error.txt', error)
        raise RuntimeError('Configuration validation failed; see private validation_error.txt')
    p = subprocess.Popen([str(BINARY), '-d', str(ROOT), '-f', str(CONFIG)],
                         env=env, stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL,
                         stderr=subprocess.DEVNULL, start_new_session=True)
    save_private(PID, str(p.pid))
    for _ in range(30):
        try:
            print('Mihomo started:', api('/version')['version'])
            print('Proxy: 127.0.0.1:17890; controller: 127.0.0.1:19090')
            return
        except (OSError, ValueError):
            if p.poll() is not None:
                raise RuntimeError('Task proxy exited during startup') from None
            time.sleep(0.5)
    raise RuntimeError('Controller did not become ready')


def configure():
    url = getpass.getpass('Paste your Clash/Mihomo HTTPS subscription (hidden): ').strip()
    parsed = urllib.parse.urlsplit(url)
    if parsed.scheme != 'https' or not parsed.hostname:
        raise ValueError('A valid HTTPS Clash/Mihomo subscription URL is required')
    old = json.loads(CONFIG.read_text()) if CONFIG.exists() else {}
    cfg = {
        'mixed-port': 17890, 'allow-lan': False, 'bind-address': '127.0.0.1',
        'mode': 'rule', 'log-level': 'silent', 'ipv6': False,
        'find-process-mode': 'off', 'external-controller': '127.0.0.1:19090',
        'secret': old.get('secret') or secrets.token_hex(32),
        'authentication': old.get('authentication') or ['glm-download:' + secrets.token_hex(24)],
        'skip-auth-prefixes': [], 'tun': {'enable': False}, 'dns': {'enable': False},
        'profile': {'store-selected': True},
        'proxy-providers': {'subscription': {
            'type': 'http', 'url': url, 'path': './providers/subscription.yaml',
            'interval': 86400, 'proxy': 'DIRECT', 'size-limit': 8388608,
            'override': {'skip-cert-verify': False},
            'header': {'User-Agent': ['clash.meta']},
            'health-check': {'enable': True, 'url': 'https://www.gstatic.com/generate_204',
                             'interval': 600, 'timeout': 5000, 'lazy': True}}},
        'proxy-groups': [
            {'name': 'Auto', 'type': 'url-test', 'use': ['subscription'],
             'url': 'https://www.gstatic.com/generate_204', 'interval': 300, 'tolerance': 100},
            {'name': 'DownloadProxy', 'type': 'select', 'proxies': ['Auto'], 'use': ['subscription']}],
        'rules': ['MATCH,DownloadProxy'],
    }
    stop()
    save_private(CONFIG, json.dumps(cfg, indent=2))
    if not BINARY.exists():
        print('Subscription saved privately. Binary download is pending; Codex can start it when ready.')
        return
    start()
    print('Subscription saved privately. Tell Codex configuration is complete; do not send the URL.')


if __name__ == '__main__':
    os.umask(0o077)
    ROOT.mkdir(mode=0o700, exist_ok=True)
    ROOT.chmod(0o700)
    parser = argparse.ArgumentParser()
    parser.add_argument('action', choices=['configure', 'start', 'stop', 'status'])
    args = parser.parse_args()
    if args.action == 'configure':
        configure()
    elif args.action == 'start':
        start()
    elif args.action == 'stop':
        stop()
        print('Task proxy stopped.')
    else:
        print(json.dumps({'configured': CONFIG.exists(), 'pid': managed_pid(),
                          'listen': '127.0.0.1:17890', 'system_proxy_modified': False}))
