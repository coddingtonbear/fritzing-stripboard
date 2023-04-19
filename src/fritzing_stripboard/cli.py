import argparse
import sys
from xml.etree import ElementTree

import yaml

from .types import BoardSpecification
from .builder import build_svg


def main(args=sys.argv):
    parser = argparse.ArgumentParser(description="Command description.")
    parser.add_argument("path", type=argparse.FileType("r"))
    args = parser.parse_args(args=args[1:])

    loaded = BoardSpecification.parse_obj(yaml.safe_load(args.path))

    svg_document = build_svg(loaded)

    print(ElementTree.tostring(svg_document).decode("utf-8"))
