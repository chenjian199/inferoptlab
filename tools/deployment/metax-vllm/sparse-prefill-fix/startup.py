"""Opt-in import hook loaded by the installed .pth file in each Python worker."""
import os

if os.environ.get('INFEROPTLAB_SPARSE_PREFILL_OFFSET64') == '1':
    import importlib.abc
    import importlib.machinery
    import sys

    class RepairLoader(importlib.abc.Loader):
        def __init__(self, wrapped):
            self.wrapped = wrapped

        def create_module(self, spec):
            return self.wrapped.create_module(spec)

        def exec_module(self, module):
            self.wrapped.exec_module(module)
            from _inferoptlab_sparse_prefill_adapter import prefill
            module.flash_mla_sparse_fwd = prefill

    class RepairFinder(importlib.abc.MetaPathFinder):
        def find_spec(self, fullname, path=None, target=None):
            if fullname != 'vllm_metax.v1.attention.backends.mla.flashmla_sparse':
                return None
            spec = importlib.machinery.PathFinder.find_spec(fullname, path)
            if spec and spec.loader:
                spec.loader = RepairLoader(spec.loader)
            return spec

    sys.meta_path.insert(0, RepairFinder())
