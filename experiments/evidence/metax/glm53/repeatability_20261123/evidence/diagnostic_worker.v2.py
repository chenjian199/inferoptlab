"""Opt-in synchronous observation, used only in separate diagnostic process D."""
from worker_provenance import Provenance


class Diagnostic(Provenance):
    def begin_probe(self, label):
        if self.rank != 0:
            return {'rank': self.rank, 'capturing': False}
        import torch
        from vllm.v1.worker.gpu.sample.sampler import Sampler
        assert label.replace('_', '').isalnum()
        self._probe = {'label': label, 'layers': {}, 'sampling': []}
        self._probe_hooks = []

        def capture(name):
            def hook(module, args, output):
                values = output if isinstance(output, (tuple, list)) else [output]
                self._probe['layers'].setdefault(name, []).append([
                    {'shape': list(v.shape), 'dtype': str(v.dtype),
                     'last': v[-1].detach().float().cpu().clone()}
                    for v in values if isinstance(v, torch.Tensor) and v.ndim > 0])
            return hook

        for name, module in self.get_model().named_modules():
            if type(module).__name__ == 'Glm5NextDecoderLayer':
                self._probe_hooks.append(module.register_forward_hook(capture(name)))
                for child_name in ['input_layernorm','post_attention_layernorm','self_attn','linear_attn','mlp']:
                    child = getattr(module, child_name, None)
                    if isinstance(child, torch.nn.Module):
                        self._probe_hooks.append(child.register_forward_hook(capture(name+'.'+child_name)))
        original = Sampler._sample_random
        self._probe_original_sampler = original
        record = self._probe

        def sampled(sampler, logits, expanded, mapping, pos, top_k, top_p, fused):
            result = original(sampler, logits, expanded, mapping, pos, top_k, top_p, fused)
            actual, processed = result
            record['sampling'].append({
                'temperature': sampler.sampling_states.temperature.np[mapping].tolist(),
                'seeds': sampler.sampling_states.seeds.np[mapping].tolist(),
                'fused': bool(fused), 'logits_dtype': str(processed.dtype),
                'processed_logits': processed.detach().float().cpu().clone(),
                'sampled': actual.detach().cpu().clone(),
                'argmax': processed.argmax(dim=-1).detach().cpu().clone(),
                'original_sampler_module': original.__module__,
            })
            return result

        Sampler._sample_random = sampled
        return {'rank': self.rank, 'hooks': len(self._probe_hooks)}

    def end_probe(self):
        if self.rank != 0:
            return {'rank': self.rank, 'capturing': False}
        import torch
        from pathlib import Path
        from vllm.v1.worker.gpu.sample.sampler import Sampler
        for handle in self._probe_hooks:
            handle.remove()
        Sampler._sample_random = self._probe_original_sampler
        directory = Path('/experiment/evidence/diagnostics/tensors')
        directory.mkdir(parents=True, exist_ok=True)
        path = directory / (self._probe['label'] + '.pt')
        assert not path.exists()
        torch.save(self._probe, path)
        result = {'rank': self.rank, 'path': str(path), 'layers': len(self._probe['layers']),
                  'sampling_calls': len(self._probe['sampling'])}
        self._probe = None
        return result
