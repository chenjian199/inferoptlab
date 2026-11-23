"""Owned subprocess groups with bounded waits and file-backed logs."""
import os
import signal
import subprocess
import time


def start(command, log, env=None):
    options = dict(stdout=log, stderr=subprocess.STDOUT, stdin=subprocess.DEVNULL, env=env, shell=False)
    if os.name == 'posix':
        options['start_new_session'] = True
    else:
        options['creationflags'] = subprocess.CREATE_NO_WINDOW
    return subprocess.Popen(command, **options)


def stop(process):
    if process is None:
        return
    if os.name == 'posix':
        # The group was created by start(); never kill by model name or port.
        try:
            os.killpg(process.pid, signal.SIGTERM)
        except ProcessLookupError:
            return
        try:
            process.wait(timeout=10)
        except subprocess.TimeoutExpired:
            pass
        try:
            os.killpg(process.pid, signal.SIGKILL)
        except ProcessLookupError:
            pass
    elif process.poll() is None:
        process.kill()
    process.wait(timeout=10)


def run(command, log_path, timeout_s, env=None):
    started = time.monotonic()
    process = None
    with log_path.open('wb') as log:
        try:
            process = start(command, log, env)
            try:
                code = process.wait(timeout=max(0.01, timeout_s))
                return dict(returncode=code, timed_out=False, elapsed_s=time.monotonic()-started)
            except subprocess.TimeoutExpired:
                return dict(returncode=None, timed_out=True, elapsed_s=time.monotonic()-started)
        finally:
            stop(process)
