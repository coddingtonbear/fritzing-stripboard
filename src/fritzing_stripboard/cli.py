import argparse
import sys
from xml.etree import ElementTree
import zipfile

import yaml

from .types import BoardSpecification
from .svg import build_svg
from .fzp import build_fzp


def main(args=sys.argv):
    parser = argparse.ArgumentParser(description="Command description.")
    parser.add_argument("path", type=argparse.FileType("r"))
    parser.add_argument("output", type=str)
    args = parser.parse_args(args=args[1:])

    loaded = BoardSpecification.parse_obj(yaml.safe_load(args.path))

    svg_document = build_svg(loaded)
    fzp_document = build_fzp(loaded)

    with zipfile.ZipFile(args.output, mode="w") as archive:
        with archive.open(f"part.{loaded.meta.label}.fzp", "w") as fzpf:
            fzpf.write(ElementTree.tostring(fzp_document))

        with archive.open(f"svg.breadboard.{loaded.meta.label}.svg", "w") as svgf:
            svgf.write(ElementTree.tostring(svg_document))
