"""Deterministic, test-independent HumanEval chat output normalization."""
import ast
import re

VERSION = 'humaneval-chat-code-v1'


def assemble(prompt, output, entry_point):
    text = output.rsplit('</think>', 1)[-1]
    if '<think>' in text:
        raise ValueError('unfinished_reasoning')
    text = text.strip('\r\n')
    if text.lstrip().startswith('```'):
        match = re.fullmatch(r'\s*```(?:python|py)?[ \t]*\r?\n(.*?)\r?\n```\s*', text, re.S | re.I)
        if not match:
            raise ValueError('ambiguous_code_fence')
        text = match.group(1)
    if not text.strip():
        raise ValueError('empty_code')
    mode = 'continuation'
    try:
        tree = ast.parse(text)
        if any(isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == entry_point
               for node in tree.body):
            mode = 'full_module_redefines_entry_point'
    except SyntaxError:
        pass
    # Keep provided imports/helpers. Full definitions override the prefix stub;
    # continuations retain indentation. Never repair based on test outcomes.
    code = prompt + ('\n' if not prompt.endswith('\n') else '') + text + '\n'
    compile(code, '<candidate>', 'exec')
    return code, mode
