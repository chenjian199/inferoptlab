import unittest
from summarize_baseline import compare


class CompareTests(unittest.TestCase):
    def test_equal_score_does_not_hide_regression(self):
        a={'a':{'passed':True},'b':{'passed':False}}
        b={'a':{'passed':False},'b':{'passed':True}}
        result=compare(a,b)
        self.assertEqual(result['regression'],['a'])
        self.assertEqual(result['improvement'],['b'])

    def test_missing_task_rejected(self):
        with self.assertRaises(ValueError):compare({'a':{'passed':True}}, {})


if __name__=='__main__':unittest.main()
