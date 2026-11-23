"""Explicit single-turn fixtures, including chat-template token accounting."""
from __future__ import annotations

import json
import random
from collections.abc import Mapping
from pathlib import Path

from tools.specs import SpecError, digest
from benchmark.io import file_hash, json_write, jsonl_write

TOKENIZER_NAMES = {'tokenizer.json','tokenizer_config.json','special_tokens_map.json','added_tokens.json',
    'vocab.json','vocab.txt','merges.txt','tokenizer.model','spiece.model','chat_template.jinja','config.json'}


def tokenizer_fingerprint(path):
    path=Path(path).resolve()
    if not path.is_dir():
        raise SpecError(f'local tokenizer directory missing: {path}')
    files={p.relative_to(path).as_posix():file_hash(p) for p in sorted(path.rglob('*'))
           if p.is_file() and (p.name in TOKENIZER_NAMES or p.suffix=='.jinja')}
    if not files:
        raise SpecError('no tokenizer artifacts found')
    return dict(path=str(path),files=files,sha256=digest(files))


def load_tokenizer(path):
    try:
        from transformers import AutoTokenizer
    except ImportError as exc:
        raise SpecError('dataset preparation requires transformers (included with benchmark/requirements.txt)') from exc
    tokenizer=AutoTokenizer.from_pretrained(str(path),local_files_only=True,trust_remote_code=False)
    if not tokenizer.chat_template:
        raise SpecError('a local chat template is required for exact input-length verification')
    return tokenizer


def token_count(tokenizer, text):
    encoded=tokenizer.apply_chat_template([dict(role='user',content=text)],tokenize=True,add_generation_prompt=True)
    # Transformers 5 returns BatchEncoding by default; older tokenizers return IDs.
    ids=encoded['input_ids'] if isinstance(encoded,Mapping) else encoded
    if not isinstance(ids,(list,tuple)) or any(not isinstance(i,int) for i in ids):
        raise SpecError('chat tokenizer must return one flat sequence of token IDs')
    return len(ids)


def prompt(tokenizer, rng, target):
    words='apple blue river stone paper light cloud green music ocean garden silver morning red book yellow city field forest water'.split()
    units=[' '+word for word in words if len(tokenizer.encode(' '+word,add_special_tokens=False))==1]
    if len(units)<4:
        raise SpecError('cannot synthesize exact-length prompts with this tokenizer; import a prepared text fixture')
    size=target-token_count(tokenizer,'')
    if size<1:
        raise SpecError('target input length is below chat-template overhead')
    parts=rng.choices(units,k=size)
    for _ in range(20):
        text=''.join(parts)
        difference=target-token_count(tokenizer,text)
        if difference==0:
            return text
        if difference>0:
            parts.extend(rng.choices(units,k=difference))
        elif len(parts)>-difference:
            del parts[difference:]
        else:
            break
    raise SpecError('could not achieve exact chat input token count; import a verified text fixture')


def prepare(workload, protocol, tokenizer_path, output, source=None, tokenizer=None):
    fingerprint=tokenizer_fingerprint(tokenizer_path)
    tokenizer=tokenizer or load_tokenizer(tokenizer_path)
    count=workload['requests']['count']
    target=workload['input']['tokens']
    seed=workload['requests']['seed']
    if not count or not target or seed is None:
        raise SpecError('resolve request count, exact input tokens and seed before preparing data')
    warmup=protocol['execution'].get('warmup_request_count')
    if warmup is None:
        raise SpecError('protocol.execution.warmup_request_count is required')
    rng=random.Random(seed)
    inputs=None
    if source:
        inputs=[json.loads(line)['text'] for line in Path(source).read_text(encoding='utf-8').splitlines() if line.strip()]
        if len(inputs)!=count:
            raise SpecError(f'imported fixture must contain exactly {count} text records')
    records=[]
    used=set()
    for phase,n in [('profiling',count),('warmup',warmup)]:
        phase_records=[]
        for index in range(n):
            text=inputs[index] if inputs is not None and phase=='profiling' else prompt(tokenizer,rng,target)
            if not isinstance(text,str) or token_count(tokenizer,text)!=target:
                raise SpecError(f'{phase}/{index}: full chat-template token length differs from {target}')
            if text in used:
                raise SpecError('duplicate prompts are not allowed for random_independent fixtures')
            used.add(text)
            phase_records.append(dict(session_id=f'{workload["id"]}-{phase}-{index:06d}',text=text))
        records.append(phase_records)
    output=Path(output)
    output.mkdir(parents=True,exist_ok=False)
    manifest=dict(format_version=1,workload_id=workload['id'],workload_sha256=digest(workload),
        input_tokens=target,output_tokens=workload['output']['tokens'],seed=seed,tokenizer=fingerprint,
        token_count_boundary='apply_chat_template(user, add_generation_prompt=True)',files={})
    for filename,rows in zip(('requests.jsonl','warmup.jsonl'),records):
        jsonl_write(output/filename,rows)
        manifest['files'][filename]=dict(sha256=file_hash(output/filename),count=len(rows),session_ids=[r['session_id'] for r in rows])
    json_write(output/'manifest.json',manifest)
    return manifest


def verify(workload, protocol, tokenizer_path, directory, retokenize=True):
    directory=Path(directory)
    try:
        manifest=json.loads((directory/'manifest.json').read_text(encoding='utf-8'))
        fingerprint=tokenizer_fingerprint(tokenizer_path)
        if manifest['tokenizer']['sha256']!=fingerprint['sha256']:
            raise SpecError('tokenizer artifact fingerprint differs from prepared fixture')
        if manifest['workload_id']!=workload['id'] or manifest['input_tokens']!=workload['input']['tokens'] or manifest['output_tokens']!=workload['output']['tokens'] or manifest['seed']!=workload['requests']['seed']:
            raise SpecError('dataset metadata differs from selected workload')
        tokenizer=load_tokenizer(tokenizer_path) if retokenize else None
        all_texts=set()
        for name,count in [('requests.jsonl',workload['requests']['count']),('warmup.jsonl',protocol['execution']['warmup_request_count'])]:
            entry=manifest['files'][name]
            if file_hash(directory/name)!=entry['sha256']:
                raise SpecError(f'dataset hash mismatch: {name}')
            rows=[json.loads(line) for line in (directory/name).read_text(encoding='utf-8').splitlines() if line.strip()]
            if len(rows)!=count or entry['count']!=count or [r['session_id'] for r in rows]!=entry['session_ids'] or len(set(entry['session_ids']))!=count:
                raise SpecError(f'dataset count/session IDs mismatch: {name}')
            for row in rows:
                if set(row)!={'session_id','text'} or not isinstance(row['text'],str):
                    raise SpecError('only session_id/text are accepted; per-request overrides are forbidden')
                if row['text'] in all_texts:
                    raise SpecError('warmup/profiling fixtures must contain distinct prompts')
                all_texts.add(row['text'])
                if tokenizer and token_count(tokenizer,row['text'])!=workload['input']['tokens']:
                    raise SpecError('actual chat-template token count differs from workload')
        expected=workload['requests']['request_set_sha256']
        if expected and expected!=manifest['files']['requests.jsonl']['sha256']:
            raise SpecError('request set does not match frozen WorkloadSpec hash')
        return manifest
    except (OSError, ValueError, KeyError, TypeError) as exc:
        raise SpecError(f'invalid/unprepared dataset at {directory}: {exc}') from exc
