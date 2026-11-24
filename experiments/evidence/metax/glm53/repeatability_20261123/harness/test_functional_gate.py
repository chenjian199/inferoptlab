import unittest
from check_functional_gate import matrix_gate


class GateTests(unittest.TestCase):
    def test_improvement_does_not_offset_stable_regression(self):
        b=[{'a':True,'b':False}]*3
        c=[{'a':False,'b':True}]*3
        self.assertEqual(matrix_gate(b,c)['status'],'fail')

    def test_flaky_worsening_requires_review(self):
        b=[{'a':True},{'a':False},{'a':True}]
        c=[{'a':True},{'a':False},{'a':False}]
        self.assertEqual(matrix_gate(b,c)['status'],'inconclusive')

    def test_unchanged_passes_functional_only(self):
        b=[{'a':True,'b':False}]*3
        self.assertEqual(matrix_gate(b,b)['status'],'pass_functional')

    def test_incomplete_repeats_rejected(self):
        with self.assertRaises(ValueError):matrix_gate([{'a':True}],[{'a':True}]*3)


if __name__=='__main__':
    unittest.main()
