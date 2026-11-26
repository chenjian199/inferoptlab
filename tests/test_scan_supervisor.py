"""Exercise recovery control flow without Docker or GPU execution."""
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch, MagicMock

from benchmark.common.io import json_write
from tools.specs import ROOT
from tools.specs import SpecError

spec=importlib.util.spec_from_file_location('scan_supervisor',ROOT/'tools/deployment/metax-vllm/supervise_scan.py')
supervisor=importlib.util.module_from_spec(spec)
spec.loader.exec_module(supervisor)


class SupervisorTests(unittest.TestCase):
    def simulate(self,outcomes,qualify=False,qualification_error=False):
        with tempfile.TemporaryDirectory() as temporary:
            root=Path(temporary)
            session=root/'experiments/session'
            calls=[]
            snapshot=dict(trials=[{},{}],content_sha256='a'*64,execution_issues=[])
            def launch(command,**kwargs):
                calls.append(command)
                count,code=outcomes[min(len(calls)-1,len(outcomes)-1)]
                output=Path(command[command.index('--out')+1])
                batch=output/'batch-synthetic'
                json_write(batch/'batch.json',dict(status='completed' if count==2 else 'completed_with_errors',
                           runs=[dict(status='completed',directory=f'run-{i}') for i in range(count)]))
                process=MagicMock(pid=42)
                process.wait.return_value=code
                process.poll.return_value=code
                return process
            with patch.object(supervisor,'ROOT',root),patch.object(supervisor,'Catalog'), \
                 patch.object(supervisor,'load_snapshot',return_value=snapshot), \
                 patch.object(supervisor,'embedded_catalog'),patch.object(supervisor,'verify_receipt') as verify, \
                 patch('benchmark.load.qualification.qualify') as startup, \
                 patch('benchmark.load.runner.lease'), \
                 patch.object(supervisor.subprocess,'Popen',side_effect=launch), \
                 patch.object(supervisor.time,'sleep'),patch('builtins.print'):
                startup_args=['--qualify-before-run'] if qualify else ['--qualification','unused']
                if qualification_error:
                    verify.side_effect=SpecError('no matching successful startup qualification')
                try:
                    result=supervisor.main(['--plan','unused',*startup_args,'--client-root','unused',
                            '--client-image','sha256:synthetic','--state-dir',str(session),'--interval','1'])
                except SpecError:
                    if qualification_error:
                        self.assertEqual(calls,[])
                        self.assertEqual(startup.call_count,1)
                    raise
                self.assertEqual(startup.call_count,1 if qualify else 0)
            return result,json.loads((session/'state.json').read_text()),calls

    def test_failed_process_resumes_same_batch_and_complete_requires_all_points(self):
        result,state,calls=self.simulate([(1,1),(2,0)])
        self.assertEqual(result,0)
        self.assertEqual(state['progress']['completed'],2)
        self.assertNotIn('--resume',calls[0])
        self.assertIn('--resume',calls[1])
        self.assertEqual(len(calls),2)

    def test_zero_exit_with_missing_points_is_not_completion(self):
        result,state,calls=self.simulate([(0,0)])
        self.assertEqual(result,1)
        self.assertEqual(state['status'],'needs_repair')
        self.assertEqual(len(calls),3)

    def test_repeated_failure_is_bounded_and_not_hidden(self):
        result,state,calls=self.simulate([(0,1)])
        self.assertEqual(result,1)
        self.assertEqual(state['status'],'needs_repair')
        self.assertEqual([x['returncode'] for x in state['attempts']],[1,1,1])

    def test_new_layouts_are_qualified_before_scanning(self):
        result,state,calls=self.simulate([(2,0)],qualify=True)
        self.assertEqual(result,0)
        self.assertEqual(Path(state['qualification']).parts[-2:],('startup','qualification.json'))
        self.assertEqual(calls[0][calls[0].index('--qualification')+1],state['qualification'])

    def test_failed_new_layout_qualification_never_starts_measurements(self):
        with self.assertRaisesRegex(SpecError,'no matching successful startup qualification'):
            self.simulate([(2,0)],qualify=True,qualification_error=True)


if __name__=='__main__':
    unittest.main()
