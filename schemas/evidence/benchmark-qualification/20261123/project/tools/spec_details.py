"""Cross-field checks for machine-inspected recipes and hardware calibration."""
from __future__ import annotations

import math
import statistics


def errors(document, catalog):
    result = []
    kind = document['kind']
    if kind == 'ModelSpec' and document.get('evidence_level') == 'inspected':
        arch, checkpoint = document['architecture'], document['checkpoint']
        text, moe = arch['text'], arch['moe']
        layers = text['num_hidden_layers']
        if arch['type'] == 'moe' and moe is None:
            result.append('MoE architecture requires inspected expert configuration')
        if arch['type'] == 'dense' and moe is not None:
            result.append('dense architecture must use null for MoE configuration')
        if moe and moe['experts_per_token'] > moe['routed_experts']:
            result.append('experts_per_token exceeds routed_experts')
        if moe and moe['first_dense_layers'] > layers:
            result.append('first_dense_layers exceeds num_hidden_layers')
        if text['layer_types'] and len(text['layer_types']) != layers:
            result.append('layer_types must contain one entry per text layer')
        if arch['context_limit_tokens'] != text['max_position_embeddings']:
            result.append('context_limit_tokens must match the inspected text config')
        compression = arch['attention_config'].get('compress_ratios')
        if compression and len(compression) != layers + arch['mtp_layers']:
            result.append('compress_ratios must cover the main and MTP layers')
        engram = arch.get('engram')
        if engram and (len(engram['layer_ids']) != len(engram['num_embeddings']) or
                       len(set(engram['layer_ids'])) != len(engram['layer_ids']) or
                       any(i >= layers for i in engram['layer_ids'])):
            result.append('Engram layer IDs and embedding sizes must match the text layers')
        linear = arch.get('linear_attention')
        if linear:
            ids = linear['layers']
            expected = [i for i, value in enumerate(text['layer_types']) if value == 'linear_attention']
            if len(ids) != len(set(ids)) or ids != expected:
                result.append('linear attention layer IDs must match layer_types')
        rows = checkpoint['storage_dtypes']
        if len({r['dtype'] for r in rows}) != len(rows):
            result.append('checkpoint dtype summaries must be unique')
        if sum(r['tensor_count'] for r in rows) != checkpoint['tensor_count']:
            result.append('checkpoint tensor_count differs from dtype totals')
        if sum(r['storage_bytes'] for r in rows) >= checkpoint['total_file_bytes']:
            result.append('checkpoint files must include space for safetensors headers')
        if checkpoint['compatibility']['status'] == 'observed_loaded' and (
            (checkpoint['index'] is not None and not checkpoint['index_matches_headers']) or checkpoint['duplicate_tensor_names']
        ):
            result.append('observed_loaded requires an unambiguous matching shard index')
        if checkpoint['format'] == 'ascend_safetensors' and checkpoint['compatibility']['status'] == 'observed_loaded':
            result.append('Ascend checkpoint cannot be marked loaded on MetaX without a separate converted recipe')
    elif kind == 'HardwareSpec' and document.get('evidence_level') == 'inspected':
        discovered = document['discovery']
        if discovered['logical_cpus'] != (discovered['cpu_sockets'] * discovered['cores_per_socket'] * discovered['threads_per_core']):
            result.append('CPU socket/core/thread counts disagree')
        for node in document['resources']['nodes']:
            devices = [d['observed'] for d in node['devices']]
            for field in ('ordinal', 'pci_bus_id', 'board_serial'):
                if len({d[field] for d in devices}) != len(devices):
                    result.append(f'duplicate observed device {field}')
            for device in devices:
                if device['observed_used_memory_bytes'] > device['memory_bytes']:
                    result.append('used GPU memory exceeds capacity')
                if device['driver_reserved_bytes'] is not None and device['driver_reserved_bytes'] > device['memory_bytes']:
                    result.append('reserved GPU memory exceeds capacity')
                if device['numa_node'] >= discovered['numa_nodes']:
                    result.append('GPU NUMA node is outside host topology')
            if node['dram_gb'] is not None and not math.isclose(node['dram_gb'] * 1e9, discovered['dram_bytes'], rel_tol=1e-8):
                result.append('dram_gb uses decimal GB and must match discovered dram_bytes')
    elif kind == 'HardwareMeasurement':
        hardware = catalog.get(document['hardware_ref'])
        devices = {d['device_id'] for n in hardware['resources']['nodes'] for d in n['devices']}
        if not set(document['device_ids']) <= devices:
            result.append('measurement device IDs are absent from hardware inventory')
        for row in document['measurements']:
            duration = statistics.median(row['samples_ms']) / 1000
            if row['metric'] == 'gemm':
                if row['shape_mnk'] is None or row['unit'] != 'TFLOPS' or row['payload_bytes'] is not None:
                    result.append('GEMM requires M/N/K and TFLOPS, without copy payload')
                    continue
                expected = 2 * math.prod(row['shape_mnk']) / duration / 1e12
            else:
                if row['payload_bytes'] is None or row['unit'] != 'GB/s' or row['shape_mnk'] is not None:
                    result.append('device_copy requires payload bytes and GB/s, without M/N/K')
                    continue
                expected = 2 * row['payload_bytes'] / duration / 1e9
            if not math.isclose(row['value'], expected, rel_tol=1e-6):
                result.append(f'{row["name"]}: value disagrees with raw timing samples and operation count')
    return result
