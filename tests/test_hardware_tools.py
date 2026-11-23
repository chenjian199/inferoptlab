"""Hardware workflow tests use recorded inventory and simulated execution, no GPU dependency."""
import copy
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import types
import unittest
from unittest.mock import patch, mock_open

from tools.hardware.config import load, validate
from tools.hardware.export import export, measurement_rows
from tools.hardware.metax import parse
from tools.hardware.runner import HERE, execute, verify, ssh
from tools.specs import ROOT, Catalog, SpecError, read

EVIDENCE = ROOT/'schemas/evidence/metax/20261123'


def json_file(name):
    return read(EVIDENCE/name)


def fixtures():
    plan = load(HERE/'plans/metax.yaml')
    plan['id'] = 'unit-hardware-baseline'
    inventory = json_file('host.json')
    calibration = json_file('calibration-v3.json')
    idle = calibration['gpu_before']
    inventory['commands']['processes'] = dict(returncode=0, stdout=idle)
    inventory['commands']['topology'] = dict(returncode=0, stdout=json_file('model-directory-and-topology.json')['topology'])
    result = calibration['result']
    result.update(physical_ordinal='0', protocol=plan['protocol'], packages=dict(torch=result['torch_version']))
    for row in result['measurements']:
        if 'shape_mnk' in row:
            m,n,k = row['shape_mnk']
            row['name'] = f'gemm_{row["dtype"].split(".")[-1]}_{m}x{n}x{k}'
        else:
            row['name'] = 'device_copy_256mib'
    attempt = dict(ordinal=0, status='measured', returncode=0, result=result,
                   before=dict(returncode=0, stdout=idle), after=dict(returncode=0, stdout=idle))
    raw = dict(hostname=inventory['hostname'], status='measured', inventory=inventory,
               selected_devices=[0], image_id=plan['hosts'][0]['image'], attempts=[attempt])
    return plan, raw


class HardwareToolsTests(unittest.TestCase):
    def test_plan_rejects_duplicate_hosts_and_unsafe_or_unsupported_options(self):
        plan, _ = fixtures()
        invalid = []
        p=copy.deepcopy(plan); p['hosts'].append(copy.deepcopy(p['hosts'][0])); invalid.append(p)
        p=copy.deepcopy(plan); p['hosts'][0]['ssh']='-oProxyCommand=bad'; invalid.append(p)
        p=copy.deepcopy(plan); p['hosts'][0]['id']='../other'; invalid.append(p)
        p=copy.deepcopy(plan); p['hosts'][0]['backend']='cuda'; invalid.append(p)
        p=copy.deepcopy(plan); p['hosts'][0]['devices']=[0,1]; p['hosts'][0]['max_devices']=1; invalid.append(p)
        p=copy.deepcopy(plan); p['protocol']['max_allocation_mib']=4; invalid.append(p)
        p=copy.deepcopy(plan); p['protocol']['repeats']=2; invalid.append(p)
        for p in invalid:
            with self.subTest(plan=p), self.assertRaises(SpecError):
                validate(p)

    def test_actual_inventory_units_identity_and_topology(self):
        _, raw = fixtures()
        parsed = parse(raw['inventory'])
        self.assertEqual(8, len(parsed['devices']))
        self.assertEqual(28, len(parsed['topology']))
        gpu0 = parsed['devices'][0]['observed']
        self.assertEqual(64*1024**3, gpu0['memory_bytes'])
        self.assertEqual('AENA2402001182', gpu0['board_serial'])
        self.assertEqual('0000:05:00.0', gpu0['pci_bus_id'])
        self.assertEqual(192, parsed['discovery']['logical_cpus'])
        self.assertNotEqual('healthy', parsed['discovery']['health'])
        broken = copy.deepcopy(raw['inventory'])
        broken['commands']['memory']['stdout'] = broken['commands']['memory']['stdout'].replace(' KB', ' mystery')
        with self.assertRaises(SpecError):
            parse(broken)
        broken = copy.deepcopy(raw['inventory'])
        broken['commands']['hwinfo']['stdout'] = broken['commands']['hwinfo']['stdout'].replace('0000:05:00.0', '0000:06:00.0')
        with self.assertRaises(SpecError):
            parse(broken)

    def test_matrix_and_protocol_must_match(self):
        plan, raw = fixtures()
        attempt = raw['attempts'][0]
        self.assertEqual(4, len(measurement_rows(attempt, plan['protocol'])))
        for change in ('missing', 'dtype', 'tf32', 'samples', 'ordinal'):
            a = copy.deepcopy(attempt)
            m = a['result']['measurements'][0]
            if change == 'missing': a['result']['measurements'].pop()
            if change == 'dtype': m['dtype'] = 'torch.float64'
            if change == 'tf32': m['allow_tf32'] = True
            if change == 'samples': m['samples_ms'].pop()
            if change == 'ordinal': a['ordinal'] = 7
            with self.subTest(change=change), self.assertRaises(SpecError):
                measurement_rows(a, plan['protocol'])

    def test_run_export_and_full_source_closure(self):
        plan, raw = fixtures()
        with tempfile.TemporaryDirectory(dir=ROOT/'runs') as tmp:
            run, out = Path(tmp)/'run', Path(tmp)/'export'
            manifest = execute(plan, run, transport=lambda *args: copy.deepcopy(raw))
            self.assertEqual('complete', manifest['status'])
            paths = export(run, out)
            self.assertEqual(12, len(paths))
            catalog = Catalog(); catalog.load()
            for path in paths:
                doc = read(path); catalog.documents[(doc['id'], doc['version'])] = doc
            for path in paths:
                doc = read(path)
                self.assertEqual([], catalog.structural_errors(doc))
                self.assertEqual([], catalog.semantic_errors(doc, verify_sources=True))
            with self.assertRaises(SpecError): export(run, out)
            # Tampered bytes must fail before any recipe is written.
            (run/'metax/result.json').write_text('{}', encoding='utf-8')
            with self.assertRaises(SpecError): export(run, Path(tmp)/'tampered')
            self.assertFalse((Path(tmp)/'tampered').exists())

    def test_export_recomputes_rate_before_writing(self):
        plan, raw = fixtures()
        raw['attempts'][0]['result']['measurements'][0]['value'] *= 8
        with tempfile.TemporaryDirectory(dir=ROOT/'runs') as tmp:
            run, out = Path(tmp)/'run', Path(tmp)/'export'
            execute(plan, run, transport=lambda *args: raw)
            with self.assertRaisesRegex(SpecError, 'raw timing'): export(run, out)
            self.assertFalse(out.exists())

    def test_incomplete_run_is_preserved_and_not_exportable(self):
        plan, _ = fixtures()
        with tempfile.TemporaryDirectory(dir=ROOT/'runs') as tmp:
            run = Path(tmp)/'run'
            execute(plan, run, transport=lambda *args: dict(status='failed', error='unreachable'))
            manifest, _ = verify(run)
            self.assertEqual('incomplete', manifest['status'])
            self.assertTrue((run/'metax/worker.py').is_file())
            with self.assertRaises(SpecError): export(run, Path(tmp)/'export')
            with self.assertRaises(FileExistsError): execute(plan, run, transport=lambda *args: {})

    def test_inspection_never_creates_measurements(self):
        plan, raw = fixtures()
        raw.update(status='inspected', attempts=[])
        with tempfile.TemporaryDirectory(dir=ROOT/'runs') as tmp:
            run = Path(tmp)/'run'
            execute(plan, run, mode='inspect', transport=lambda *args: raw)
            paths = export(run, Path(tmp)/'export')
            self.assertEqual(10, len(paths))
            self.assertNotIn('HardwareMeasurement', {read(p)['kind'] for p in paths})

    def test_manifest_cannot_omit_executed_sources(self):
        plan, raw = fixtures()
        with tempfile.TemporaryDirectory() as tmp:
            run = Path(tmp)/'run'; execute(plan, run, transport=lambda *args: raw)
            manifest = read(run/'manifest.json'); del manifest['files']['benchmark.py']
            (run/'manifest.json').write_text(json.dumps(manifest), encoding='utf-8')
            with self.assertRaises(SpecError): verify(run)

    def remote(self, raw, plan, mode='run', docker=None):
        namespace = {'__name__': '_test_worker'}
        fake_fcntl = types.SimpleNamespace(LOCK_EX=1, LOCK_NB=2, flock=lambda *args: None)
        with patch.dict(sys.modules, fcntl=fake_fcntl):
            exec((HERE/'remote.py').read_text(encoding='utf-8'), namespace)
        namespace['os'] = types.SimpleNamespace(uname=lambda: types.SimpleNamespace(nodename='test'))
        namespace['open'] = mock_open()
        inventory_code = 'def inventory(): return '+repr(raw['inventory'])+'\ndef command(args): return '+repr(raw['attempts'][0]['before'])
        payload = dict(host=plan['hosts'][0], protocol=plan['protocol'], mode=mode, inventory_code=inventory_code,
                       benchmark_code=(HERE/'probes/torch_bench.py').read_text(encoding='utf-8'))
        with patch('subprocess.run', side_effect=docker) as mock:
            result = namespace['run'](payload)
            return result, mock.call_args_list

    def test_remote_malformed_and_busy_process_tables_never_start_gpu_work(self):
        plan, raw = fixtures()
        raw['inventory']['commands']['processes']['stdout']='unrecognized table'
        result, calls = self.remote(raw, plan)
        self.assertEqual('failed', result['status']); self.assertFalse(calls)
        plan, raw = fixtures()
        busy = raw['attempts'][0]['before']['stdout'].replace('no process found', '| 0 1234 python |')
        raw['attempts'][0]['before']['stdout'] = busy
        def docker(args, **kwargs):
            return subprocess.CompletedProcess(args, 0, plan['hosts'][0]['image']+'\n', '')
        result, calls = self.remote(raw, plan, docker=docker)
        self.assertEqual('blocked', result['attempts'][0]['status'])
        self.assertEqual(1, len(calls))  # image identity only

    def test_remote_timeout_cleans_only_its_own_container(self):
        plan, raw = fixtures()
        def docker(args, **kwargs):
            if args[1] == 'run': raise subprocess.TimeoutExpired(args, 150, output=b'partial output')
            return subprocess.CompletedProcess(args, 0, plan['hosts'][0]['image']+'\n', '')
        result, calls = self.remote(raw, plan, docker=docker)
        self.assertEqual('incomplete', result['status'])
        attempt = result['attempts'][0]
        self.assertEqual('timeout', attempt['status'])
        self.assertEqual('partial output', attempt['stdout'])
        self.assertEqual(['docker', 'rm', '-f', attempt['container_name']], calls[-1].args[0])
        self.assertTrue(attempt['container_name'].startswith('inferoptlab-hardware-'))

    def test_remote_all_device_limit_prevents_work(self):
        plan, raw = fixtures()
        plan['hosts'][0].update(devices='all', max_devices=1)
        result, calls = self.remote(raw, plan)
        self.assertEqual('failed', result['status']); self.assertFalse(calls)
        self.assertIn('max_devices', result['error'])

    def test_ssh_failures_preserve_diagnostics(self):
        response = subprocess.CompletedProcess([], 0, b'not json', b'warning')
        with patch('subprocess.run', return_value=response):
            result = ssh('metax', b'probe', 30)
        self.assertEqual('failed', result['status'])
        self.assertEqual('not json', result['stdout'])
        with patch('subprocess.run', side_effect=subprocess.TimeoutExpired([], 30, output=b'partial', stderr=b'error')):
            result = ssh('metax', b'probe', 30)
        self.assertEqual('partial', result['stdout'])
        self.assertEqual('error', result['stderr'])

    def test_multiple_hosts_run_sequentially_and_preserve_each_result(self):
        plan, raw = fixtures()
        second = copy.deepcopy(plan['hosts'][0]); second.update(id='second', ssh='second')
        plan['hosts'].append(second)
        calls = []
        def transport(host, script, timeout):
            calls.append(host)
            return copy.deepcopy(raw) if host == 'metax' else dict(status='blocked', error='occupied')
        with tempfile.TemporaryDirectory() as tmp:
            run = Path(tmp)/'run'
            manifest = execute(plan, run, transport=transport)
            self.assertEqual(['metax', 'second'], calls)
            self.assertEqual(['measured', 'blocked'], [h['status'] for h in manifest['hosts']])
            self.assertEqual('incomplete', manifest['status'])
            verify(run)

    def test_remote_cleanup_failure_invalidates_measurement(self):
        plan, raw = fixtures()
        def docker(args, **kwargs):
            if args[1] == 'run':
                return subprocess.CompletedProcess(args, 0, json.dumps(raw['attempts'][0]['result']).encode(), b'')
            if args[1] == 'rm':
                return subprocess.CompletedProcess(args, 1, '', 'Docker unavailable')
            return subprocess.CompletedProcess(args, 0, plan['hosts'][0]['image']+'\n', '')
        result, calls = self.remote(raw, plan, docker=docker)
        self.assertEqual('incomplete', result['status'])
        self.assertEqual('cleanup_failed', result['attempts'][0]['status'])


if __name__ == '__main__':
    unittest.main()
