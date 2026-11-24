import unittest
from code_adapter import assemble


class AdapterTests(unittest.TestCase):
    prompt='from typing import List\ndef f(x):\n    """Example."""\n'

    def test_body(self):
        code,mode=assemble(self.prompt,'    return x + 1','f')
        ns={};exec(code,ns);self.assertEqual(ns['f'](1),2)
        self.assertEqual(mode,'continuation')

    def test_full_function_after_reasoning(self):
        code,mode=assemble(self.prompt,'reasoning</think>\n```python\ndef f(x):\n    return x+2\n```','f')
        ns={};exec(code,ns);self.assertEqual(ns['f'](1),3)
        self.assertEqual(mode,'full_module_redefines_entry_point')

    def test_no_indentation_repair(self):
        with self.assertRaises(SyntaxError):assemble(self.prompt,'return x','f')

    def test_unfinished_reasoning(self):
        with self.assertRaises(ValueError):assemble(self.prompt,'<think>unfinished','f')

    def test_ambiguous_fences_rejected(self):
        with self.assertRaises(ValueError):assemble(self.prompt,'```python\n    return x\n```\nexplanation','f')


if __name__=='__main__':unittest.main()
