import argparse
from pathlib import Path

from routeros_diff.parser import RouterOSConfig


def run():
    parser = argparse.ArgumentParser(
        description="Diff two RouterOS configuration files"
    )
    parser.add_argument("old", metavar="OLD", type=str, help="Path to the old file")
    parser.add_argument("new", metavar="NEW", type=str, help="Path to the new file")
    args = parser.parse_args()

    old = RouterOSConfig.parse(Path(args.old).read_text())
    new = RouterOSConfig.parse(Path(args.new).read_text())
    print(old.diff(new))
