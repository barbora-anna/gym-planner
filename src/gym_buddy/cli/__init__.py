"""The `gym` command: what the Coach calls for numbers, history and the session page.

Exit codes: 0 done, 1 error or an ambiguous exercise (candidates listed), 2 needs
`--confirm` (nothing was written).
"""

import argparse
import sys

from gym_buddy import __version__

from . import calc, init, lift, log, render, volume
from ._common import UserError


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="gym", description="gym-buddy strength toolkit")
    parser.add_argument("--version", action="version", version=f"gym {__version__}")
    sub = parser.add_subparsers(dest="command")
    for module in (init, log, lift, calc, volume, render):
        module.register(sub)
    args = parser.parse_args(sys.argv[1:] if argv is None else argv)
    func = getattr(args, "func", None)
    if func is None:
        parser.print_help()
        return 0
    try:
        return func(args)
    except UserError as e:
        print(f"ERROR  {e}")
        return 1

