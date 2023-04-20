import argparse
import sys

import yaml

from .types import BoardSpecification
from .zip import build_zip


def main(args=sys.argv):
    parser = argparse.ArgumentParser(description="Command description.")
    parser.add_argument("path", type=argparse.FileType("r"))
    parser.add_argument("output", type=str)
    args = parser.parse_args(args=args[1:])

    loaded = BoardSpecification.parse_obj(yaml.safe_load(args.path))

    build_zip(loaded, args.output)
