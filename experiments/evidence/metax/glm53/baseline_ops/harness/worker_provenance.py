"""Read-only worker provenance extension for the inference acceptance run."""
class Provenance:
    def start_layer_trace(self, label):
        import torch
        if getattr(self, 'rank', -1) != 0:
            return 'rank skipped'
        assert label in ('cached', 'prefill')
        self._glm_trace = {}
        self._glm_trace_label = label
        self._glm_trace_handles = []
        self._glm_trace_originals = []
        def snapshot(values):
            values = values if isinstance(values, (tuple, list)) else (values,)
            return [{'shape': tuple(v.shape), 'last': v[-1].detach().float().cpu().clone()}
                    for v in values if isinstance(v, torch.Tensor) and v.ndim > 0]
        def hook(name):
            def capture(module, args, kwargs, output):
                values = output if isinstance(output, (tuple, list)) else (output,)
                tensors = [v for v in values if isinstance(v, torch.Tensor) and v.ndim > 0]
                self._glm_trace.setdefault(name, []).append([
                    {'shape': tuple(v.shape), 'last': v[-1].detach().float().cpu().clone()}
                    for v in tensors])
            return capture
        for name, module in self.get_model().named_modules():
            if type(module).__name__ == 'Glm5NextDecoderLayer':
                self._glm_trace_handles.append(module.register_forward_hook(hook(name), with_kwargs=True))
                self._glm_trace_handles.append(module.self_attn.register_forward_hook(hook(name+'.self_attn'), with_kwargs=True))
            if '.layers.3.self_attn.' in name:
                self._glm_trace_handles.append(module.register_forward_hook(hook(name), with_kwargs=True))
                for method in ('forward_impl', '_v_up_proj'):
                    if hasattr(module, method):
                        original = getattr(module, method)
                        key = name+'.'+method
                        def wrapped(*args, _orig=original, _key=key, **kwargs):
                            self._glm_trace.setdefault(_key+'.inputs', []).append(snapshot(args))
                            result = _orig(*args, **kwargs)
                            self._glm_trace.setdefault(_key+'.output_buffer', []).append(snapshot(kwargs.get('output', kwargs.get('out'))))
                            self._glm_trace.setdefault(_key+'.returned', []).append(snapshot(result))
                            return result
                        self._glm_trace_originals.append((module, method, original))
                        setattr(module, method, wrapped)
        return {'hooks': len(self._glm_trace_handles)}

    def stop_layer_trace(self):
        import torch
        if getattr(self, 'rank', -1) != 0:
            return 'rank skipped'
        for handle in self._glm_trace_handles:
            handle.remove()
        for module, method, original in self._glm_trace_originals:
            setattr(module, method, original)
        path = '/work/evidence/layer_trace_'+self._glm_trace_label+'.pt'
        torch.save(self._glm_trace, path)
        self._glm_trace_handles = []
        self._glm_trace = {}
        return path

    def deployment_provenance(self):
        import importlib.metadata as md
        import os
        from pathlib import Path
        import torch
        import vllm
        import vllm_metax
        from collections import Counter
        model = self.get_model()
        dtype_numel = Counter()
        quant_classes = Counter()
        indexer_dtypes = Counter()
        mla_int8_scales = []
        for name, module in model.named_modules():
            weight = getattr(module, 'weight', None)
            if ('.self_attn.' in name and name.rsplit('.', 1)[-1] in
                    ('fused_qkv_a_proj', 'q_b_proj', 'o_proj') and
                    isinstance(weight, torch.Tensor) and weight.dtype == torch.int8):
                scale = module.weight_scale
                mla_int8_scales.append({'module': name, 'numel': scale.numel(),
                    'finite_positive': bool((torch.isfinite(scale) & (scale > 0)).all()),
                    'min': float(scale.min()), 'max': float(scale.max())})
        for parameter in model.parameters():
            dtype_numel[str(parameter.dtype)] += parameter.numel()
        for module in model.modules():
            indexer_dtype = getattr(module, 'indexer_kv_dtype', None)
            if indexer_dtype is not None:
                indexer_dtypes[str(indexer_dtype)] += 1
            method = getattr(module, 'quant_method', None)
            for obj in [method, getattr(method, 'scheme', None), getattr(module, 'scheme', None)]:
                if obj is not None:
                    quant_classes[f'{type(obj).__module__}.{type(obj).__name__}'] += 1
        return {
            'pid': os.getpid(),
            'rank': getattr(self, 'rank', None),
            'device': torch.cuda.current_device(),
            'model_runner_class': f'{type(self.model_runner).__module__}.{type(self.model_runner).__name__}',
            'use_v2_model_runner': getattr(self, 'use_v2_model_runner', None),
            'vllm_file': vllm.__file__,
            'plugin_file': vllm_metax.__file__,
            'versions': {k: md.version(k) for k in ['vllm','vllm-metax','torch','triton','mcoplib']},
            'kernel_provider_flag': os.environ.get('USE_PRECOMPILED_KERNEL'),
            'parameter_dtype_numel': dict(dtype_numel),
            'quantization_classes': dict(quant_classes),
            'resolved_indexer_dtypes': dict(indexer_dtypes),
            'mla_int8_scales': mla_int8_scales,
            'native_libraries': sorted({line.split()[-1] for line in Path('/proc/self/maps').read_text().splitlines()
                                       if any(k in line for k in ['mcoplib','mcruntime','mccl','cumem_allocator'])})}
