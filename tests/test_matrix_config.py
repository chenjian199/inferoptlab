from pathlib import Path
import unittest

from benchmark.load.matrix_config import deployment_specs, expand
from benchmark.load.adapters.vllm import server_arguments
from tools.specs import read


class MatrixConfigTests(unittest.TestCase):
    def test_current_single_file_generates_all_48_commands(self):
        matrix = read(Path(__file__).resolve().parents[1]/'benchmark-matrix.yaml')
        rows = expand(matrix)
        self.assertEqual(len(rows), 48)
        for row in rows:
            dep, runtime = deployment_specs(matrix, row, Path('/tmp/cache'))
            args = server_arguments(dep, runtime)
            self.assertEqual(args[args.index('--max-model-len')+1], 'auto')
            self.assertEqual('--enable-expert-parallel' in args, row['enable_expert_parallel'])
            self.assertNotIn('--profiler-config', args)


if __name__ == '__main__':
    unittest.main()
