"""Carry an explicit DP rank from an Inputs JSON fixture to AIPerf Turn headers.

Only enabled by cached Decode AIPerf subprocesses. The private field is removed
before payload serialization; all request scheduling and measurements are AIPerf's.
"""
import importlib.abc
import importlib.machinery
import sys
from pathlib import Path


def local_tokenizer(module):
    """AIPerf's offline snapshot resolver must accept an existing local path.

    Hub IDs still use AIPerf's original resolver. Do not substitute a tokenizer
    or change token counting; this only avoids sending a path to snapshot_download.
    """
    original = module.Tokenizer._resolve_local_snapshot
    def resolve(cls, name, revision):
        path = Path(name)
        if path.is_dir():
            return str(path.resolve())
        return original(name, revision)
    module.Tokenizer._resolve_local_snapshot = classmethod(resolve)


def attach_ranks(module):
    cls = module.InputsJsonPayloadLoader
    original = cls.convert_to_conversations

    def convert(self, data):
        conversations = original(self, data)
        for conversation in conversations:
            for turn in conversation.turns:
                rank = turn.raw_payload.pop('_inferoptlab_dp_rank')
                if type(rank) is not int or rank < 0:
                    raise ValueError('cached Decode requires a nonnegative explicit DP rank')
                turn.extra_headers = {'X-data-parallel-rank': str(rank),
                    'X-Request-ID': turn.raw_payload['request_id']}
        return conversations

    cls.convert_to_conversations = convert


def preserve_headers(module):
    # AIPerf 0.12's PAYLOAD_BYTES index stores only body/max_tokens/timestamp;
    # it drops Turn.extra_headers. The CONVERSATION path preserves them.
    original = module.DatasetManager._select_mmap_format
    def select(self, conversations):
        chosen = original(self, conversations)
        if any(turn.extra_headers for conv in conversations for turn in conv.turns):
            return module.MemoryMapFormat.CONVERSATION
        return chosen
    module.DatasetManager._select_mmap_format = select


TARGETS = {'aiperf.dataset.loader.inputs_json': attach_ranks,
           'aiperf.dataset.dataset_manager': preserve_headers,
           'aiperf.common.tokenizer': local_tokenizer}


class Loader(importlib.abc.Loader):
    def __init__(self, wrapped, callback):
        self.wrapped, self.callback = wrapped, callback

    def create_module(self, spec):
        return self.wrapped.create_module(spec)

    def exec_module(self, module):
        self.wrapped.exec_module(module)
        self.callback(module)


class Finder(importlib.abc.MetaPathFinder):
    def find_spec(self, fullname, path=None, target=None):
        if fullname not in TARGETS:
            return None
        spec = importlib.machinery.PathFinder.find_spec(fullname, path)
        if spec and spec.loader:
            spec.loader = Loader(spec.loader,TARGETS[fullname])
        return spec


sys.meta_path.insert(0, Finder())
