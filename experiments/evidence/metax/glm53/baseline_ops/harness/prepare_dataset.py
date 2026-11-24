"""Pin and prepare official HumanEval without executing dataset code."""
import argparse
import hashlib
import json
from pathlib import Path
import urllib.request

REVISION = '7dce6050a7d6d172f3cc5c32aa97f52fa1a2e544'
ROOT = Path(__file__).resolve().parents[1]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_json(path, obj):
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--root', type=Path, default=ROOT)
    args = parser.parse_args()
    root = args.root.resolve()
    raw = root / 'datasets/raw' / REVISION
    prepared = root / 'datasets/prepared' / REVISION
    raw.mkdir(parents=True, exist_ok=True)
    prepared.mkdir(parents=True, exist_ok=True)
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
    entries = []
    for remote, local in [('README.md', 'README.md'),
                          ('openai_humaneval/test-00000-of-00001.parquet', 'test.parquet')]:
        url = f'https://huggingface.co/datasets/openai/openai_humaneval/resolve/{REVISION}/{remote}'
        path = raw / local
        if not path.exists():
            with opener.open(url, timeout=90) as response:
                payload = response.read()
            temp = path.with_suffix(path.suffix + '.partial')
            temp.write_bytes(payload)
            temp.replace(path)
        entries.append(dict(path=path.relative_to(root).as_posix(), url=url, sha256=sha(path), bytes=path.stat().st_size))
    import pyarrow.parquet as pq
    rows = pq.read_table(raw / 'test.parquet').to_pylist()
    assert len(rows) == 164 and len({r['task_id'] for r in rows}) == 164
    assert {r['task_id'] for r in rows} == {f'HumanEval/{i}' for i in range(164)}
    rows.sort(key=lambda r: int(r['task_id'].split('/')[1]))
    for row in rows:
        assert set(row) == {'task_id', 'prompt', 'canonical_solution', 'test', 'entry_point'}
        assert all(isinstance(v, str) for v in row.values())
    ids = [r['task_id'] for r in rows]
    smoke = sorted(ids, key=lambda x: (hashlib.sha256(('glm53-humaneval-smoke-v1:' + x).encode()).hexdigest(), x))[:32]
    outputs = []
    for filename, fields in [('prompts.jsonl', ['task_id', 'prompt']), ('scoring.jsonl', list(rows[0]))]:
        p = prepared / filename
        text = ''.join(json.dumps({k: row[k] for k in fields}, ensure_ascii=False) + '\n' for row in rows)
        p.write_text(text, encoding='utf-8')
        outputs.append(dict(path=p.relative_to(root).as_posix(), sha256=sha(p), bytes=p.stat().st_size))
    selection = prepared / 'selection.json'
    write_json(selection, dict(all=ids, smoke32=smoke))
    outputs.append(dict(path=selection.relative_to(root).as_posix(), sha256=sha(selection), bytes=selection.stat().st_size))
    manifest = dict(schema_version=1, status='prepared', dataset_id='openai/openai_humaneval',
                    split='test', revision=REVISION, expected_task_count=164, actual_task_count=len(rows),
                    task_ids=ids, task_ids_sha256=hashlib.sha256('\n'.join(ids).encode()).hexdigest(),
                    smoke_task_ids=smoke, raw_files=entries, prepared_files=outputs,
                    license_observed='MIT', license_evidence=entries[0]['path'],
                    generator_inputs='prompts.jsonl contains task_id/prompt only; scoring.jsonl must not be mounted into generation container.',
                    tokenizer_revision=None, chat_template_sha256=None)
    write_json(root / 'datasets/humaneval/manifest.json', manifest)
    print(json.dumps(dict(revision=REVISION, tasks=len(rows), smoke=len(smoke), files=entries + outputs), indent=2))


if __name__ == '__main__':
    main()
