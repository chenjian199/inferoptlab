"""Run the existing benchmark CLI using the independent AIPerf client environment.

Model paths and server images come from the plan's recipe closure. Docker access
allows the vLLM adapter to launch and stop only its own labelled containers.
"""
import argparse
import os
import subprocess
import sys
import uuid
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
from tools.specs import Catalog, SpecError
from benchmark.load.cli import load_snapshot
from benchmark.load.planner import embedded_catalog


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--client-root', type=Path, required=True, help='Existing directory containing venv/bin/python')
    parser.add_argument('--client-image', required=True, help='Pinned image in which the client venv was installed')
    parser.add_argument('action', choices=['plan', 'prepare', 'run', 'select'])
    parser.add_argument('plan', type=Path)
    parser.add_argument('--qualification', type=Path)
    parser.add_argument('--out', type=Path)
    parser.add_argument('--resume', type=Path, help='Existing batch to resume using its archived snapshot')
    parser.add_argument('--skip-failed-configurations', action='store_true')
    parser.add_argument('--client-name', help='Unique owned client container name for supervision')
    args = parser.parse_args()
    client = args.client_root.resolve(strict=True)
    # The interpreter symlink resolves inside CLIENT_IMAGE, not on the host.
    if not os.path.lexists(client/'venv/bin/python'):
        raise SpecError('client venv is missing')
    catalog = Catalog(ROOT); catalog.load()
    snapshot = load_snapshot(catalog, args.plan)
    embedded = embedded_catalog(catalog, snapshot)
    plan = embedded.get(snapshot['plan_ref'])
    deps = [embedded.get(r) for r in plan['deployment_refs']]
    cmd = ['docker', 'run', '--rm', '--pull=never', '--network=host',
           '--name', args.client_name or ('inferoptlab-client-' + uuid.uuid4().hex[:12]),
           '--label', 'io.inferoptlab.role=benchmark-client',
           '--user', f'{os.getuid()}:{os.getgid()}',
           '--mount', f'type=bind,source={ROOT},target={ROOT}',
           '--mount', f'type=bind,source={client},target=/work',
           '--mount', 'type=bind,source=/var/run/docker.sock,target=/var/run/docker.sock',
           '--mount', 'type=bind,source=/usr/bin/docker,target=/usr/bin/docker,readonly',
           '--group-add', str(os.stat('/var/run/docker.sock').st_gid),
           '--device=/dev/mxcd', '--device=/dev/dri', '--workdir', str(ROOT),
           '-e', 'HF_HUB_OFFLINE=', '-e', 'TRANSFORMERS_OFFLINE=', '-e', 'HOME=/work',
           '-e', f'PYTHONPATH={ROOT}', '-e', 'PATH=/work/venv/bin:/opt/conda/bin:/opt/mxdriver/bin:/opt/maca/bin:/usr/local/bin:/usr/bin:/bin']
    models = {str(Path(d['serving']['model_path']).resolve(strict=True)) for d in deps}
    tokenizers = {d['serving']['tokenizer_path'] for d in deps}
    if tokenizers != models:
        raise SpecError('client wrapper requires tokenizer_path equal to model_path')
    for model in sorted(models):
        cmd += ['--mount', f'type=bind,source={model},target={model},readonly']
    for cache in sorted({d['serving']['cache_dir'] for d in deps if d['serving'].get('cache_dir')}):
        Path(cache).mkdir(parents=True, exist_ok=True)
        cmd += ['--mount', f'type=bind,source={cache},target={cache}']
    cmd += ['--entrypoint', '/work/venv/bin/python', args.client_image,
            '-u', '-m', 'benchmark.load', '--root', str(ROOT), args.action, str(args.plan.resolve())]
    if args.action == 'prepare':
        if len(tokenizers) != 1:
            raise SpecError('prepare requires one tokenizer across deployments')
        cmd += ['--tokenizer', next(iter(tokenizers))]
    if args.qualification:
        cmd += ['--qualification', str(args.qualification.resolve())]
    if args.out:
        cmd += ['--out', str(args.out.resolve())]
    if args.resume:
        if args.action != 'run':
            raise SpecError('--resume is only supported for run')
        cmd += ['--resume', str(args.resume.resolve())]
    if args.skip_failed_configurations:
        if args.action != 'run':
            raise SpecError('--skip-failed-configurations is only supported for run')
        cmd += ['--skip-failed-configurations']
    return subprocess.run(cmd, check=False).returncode


if __name__ == '__main__':
    raise SystemExit(main())
