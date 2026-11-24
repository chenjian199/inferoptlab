"""Freeze the passed, idle task environment; never alter the existing dcc."""
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path('/home/metax/glm53-vllm032')
NAME = 'glm53-vllm032'
TAG = 'glm53-vllm032:verified-20261122'


def main():
    report = json.loads((ROOT/'evidence/inference_smoke.json').read_text())
    assert report['passed'] and len(report['workers']) == 8
    run = json.loads((ROOT/'evidence/inference_scale_fixed_run.json').read_text())
    assert run['exit_code'] == 0
    assert report['runner_override'] == '1'
    assert report['settings']['max_num_seqs'] == 1
    assert report['settings']['async_scheduling'] is False
    inspect = json.loads(subprocess.check_output(['docker', 'inspect', NAME]))[0]
    assert inspect['Config']['Labels']['com.codex.task'] == NAME
    dcc = json.loads(subprocess.check_output(['docker', 'inspect', 'dcc']))[0]
    assert dcc['Id'] == '3c856edd12bc08ba2fb33219093ad3986b26c9524a68523e29da0a0f1e4ac9fa'
    processes = subprocess.check_output(['docker', 'top', NAME, '-eo', 'pid,args'], text=True)
    assert [line.split(None, 1)[1].strip() for line in processes.splitlines()[1:]] == ['sleep infinity'], processes
    dest = ROOT/'baseline'
    dest.mkdir(exist_ok=True)
    archive = dest/'sources-20261122.tar.gz'
    if not archive.exists():
        temporary = dest/'sources-20261122.tar.gz.partial'
        assert not temporary.exists(), 'Inspect a previous partial archive before retrying'
        subprocess.run(['tar', '--exclude=.git', '--exclude=__pycache__',
                        '--exclude=.pytest_cache', '--exclude=.ruff_cache',
                        '--exclude=.mypy_cache', '-czf', str(temporary),
                        '-C', str(ROOT/'src'), 'vllm', 'vllm-metax'], check=True)
        temporary.rename(archive)
    subprocess.run(['tar', '-tzf', str(archive)], stdout=subprocess.DEVNULL, check=True)
    hasher = hashlib.sha256()
    with archive.open('rb') as stream:
        for chunk in iter(lambda: stream.read(8 * 1024 * 1024), b''):
            hasher.update(chunk)
    digest = hasher.hexdigest()
    print('SOURCE_ARCHIVE', archive, digest, flush=True)
    existing = subprocess.run(['docker', 'image', 'inspect', TAG], capture_output=True)
    assert existing.returncode != 0, 'Refusing to overwrite an existing baseline tag'
    commit_output = subprocess.check_output([
        'docker', 'commit', '--no-pause',
        '--change', 'LABEL com.codex.validation=GLM-5.3-Flash-W8A8-TP8-passed',
        '--change', f'LABEL com.codex.source-archive-sha256={digest}',
        NAME, TAG], text=True)
    image_ids = [line.strip() for line in commit_output.splitlines()
                 if line.strip().startswith('sha256:')]
    assert len(image_ids) == 1, commit_output
    image_id = image_ids[0]
    image = json.loads(subprocess.check_output(['docker', 'image', 'inspect', image_id]))[0]
    result = {'tag': TAG, 'image_id': image_id, 'size_bytes': image['Size'],
              'source_archive': str(archive), 'source_archive_sha256': digest,
              'note': 'Local dependency image. Editable source and compiled plugin allocator are in the matching source archive; weights, scripts, evidence and source remain bind mounts. No model weights or proxy subscription are included.',
              'dcc_id': dcc['Id'], 'dcc_image_id': dcc['Image']}
    (ROOT/'evidence/frozen_baseline.json').write_text(json.dumps(result, indent=2))
    print(json.dumps(result, indent=2), flush=True)


if __name__ == '__main__':
    main()
