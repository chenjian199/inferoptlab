"""Dispatch the three explicit benchmark modules."""
import argparse
import importlib
import sys


MODULES = {
    "load": "benchmark.load.cli",
    "accuracy": "benchmark.accuracy.cli",
    "breakdown": "benchmark.breakdown.cli",
}


def main(argv=None):
    args = list(sys.argv[1:] if argv is None else argv)
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("module", choices=MODULES)
    if not args or args[0] in {"-h", "--help"}:
        parser.print_help()
        return 0
    module = parser.parse_args(args[:1]).module
    return importlib.import_module(MODULES[module]).main(args[1:])
