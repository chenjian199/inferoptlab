import unittest
from analyze_repeats import first_difference, compare


class AnalysisTests(unittest.TestCase):
    def test_termination_difference(self):
        self.assertEqual(first_difference([1,2],[1,2,3]),2)
        self.assertIsNone(first_difference([1,2],[1,2]))

    def test_first_divergence_before_cascade(self):
        self.assertEqual(first_difference([1,2,3,4],[1,7,8,9]),1)

    def test_equal_aggregate_score_cannot_hide_regression(self):
        outputs = {'a':{'output_token_ids':[1]},'b':{'output_token_ids':[2]}}
        before = {'a':{'passed':True},'b':{'passed':False}}
        after = {'a':{'passed':False},'b':{'passed':True}}
        result = compare(outputs,outputs,before,after)
        self.assertEqual(result['score_transitions']['regression'],['a'])
        self.assertEqual(result['score_transitions']['improvement'],['b'])


if __name__ == '__main__':
    unittest.main()
