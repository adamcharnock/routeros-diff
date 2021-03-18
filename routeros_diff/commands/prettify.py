import argparse
from pathlib import Path

from routeros_diff.parser import RouterOSConfig


def run():
    parser = argparse.ArgumentParser(
        description="Diff two RouterOS configuration files"
    )
    parser.add_argument(
        "file", metavar="FILE", type=str, help="Path to the RouterOS configuration file"
    )
    args = parser.parse_args()

    print(RouterOSConfig.parse(Path(args.file).read_text()))
