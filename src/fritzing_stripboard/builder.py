import re
from xml.etree import ElementTree
from typing import Iterable

from .constants import DEFAULT_PITCH
from .types import BoardSpecification, GridDefinition, XYDrilledBus


class InvalidCellRange(Exception):
    pass


class InvalidCell(Exception):
    pass


def convert_cell_to_coordinate(cell: str) -> tuple[int, int]:
    position_parts_match = re.compile(r"([A-Z]+)(\d+)").match(cell)
    if not position_parts_match:
        raise InvalidCell(cell)
    letters, numbers = position_parts_match.groups()

    y = int(numbers)
    x = 0
    for letter in letters:
        x += ord(letter) - ord("A")

    return x, y


def convert_coordinate_to_position(
    coordinate: tuple[int, int],
    origin: tuple[float, float] = (0, 0),
    pitch: float = DEFAULT_PITCH,
) -> tuple[float, float]:
    x = coordinate[0]
    y = coordinate[1]

    return x * pitch + pitch / 2 + origin[0], y * pitch + pitch / 2 + origin[1]


def get_drill_positions_in_cell_range(
    start: str,
    end: str,
    origin: tuple[float, float] = (0, 0),
    pitch: float = DEFAULT_PITCH,
) -> Iterable[tuple[float, float]]:
    start_x, start_y = convert_cell_to_coordinate(start)
    end_x, end_y = convert_cell_to_coordinate(end)

    x_offset = min(start_x, end_x)
    y_offset = min(start_y, end_y)
    for x in range(abs(end_x - start_x) + 1):
        for y in range(abs(end_y - start_y) + 1):
            position = convert_coordinate_to_position(
                (x + x_offset, y + y_offset), origin=origin, pitch=pitch
            )
            yield position


def build_svg(board: BoardSpecification) -> ElementTree.Element:
    root = ElementTree.Element(
        "svg",
        attrib={
            "width": f"{board.width}mm",
            "height": f"{board.height}mm",
            "viewbox": f"0 0 {board.width} {board.height}",
        },
    )
    g = ElementTree.SubElement(root, "g", attrib={"id": "breadboard"})

    ElementTree.SubElement(
        g,
        "path",
        attrib={
            "id": "boardoutline",
            "strokewidth": "0",
            "stroke": "none",
            "fill": "#deb675",
            "fill-opacity": "1",
            "d": f"""
                M0,0
                L{board.width},0 {board.width},{board.height} 0,{board.height} 0,0
            """,
        },
    )

    for component in board.board:
        if isinstance(component, GridDefinition):
            for item in component.grid.components:
                if isinstance(item, XYDrilledBus):
                    start, end = item.drilled.split(":")

                    start_x, start_y = convert_coordinate_to_position(
                        convert_cell_to_coordinate(start),
                        origin=component.grid.origin,
                        pitch=component.grid.pitch,
                    )
                    end_x, end_y = convert_coordinate_to_position(
                        convert_cell_to_coordinate(end),
                        origin=component.grid.origin,
                        pitch=component.grid.pitch,
                    )

                    if not (start_x == end_x or end_y == start_y):
                        raise InvalidCellRange(item.drilled)

                    ElementTree.SubElement(
                        g,
                        "line",
                        attrib={
                            "x1": str(start_x),
                            "y1": str(start_y),
                            "x2": str(end_x),
                            "y2": str(end_y),
                            "stroke": "brown",
                            "stroke-width": "1.5",
                            "style": "stroke-linecap:round; stroke-opacity: 0.5;",
                        },
                    )

                    for drill_x, drill_y in get_drill_positions_in_cell_range(
                        start,
                        end,
                        origin=component.grid.origin,
                        pitch=component.grid.pitch,
                    ):
                        ElementTree.SubElement(
                            g,
                            "circle",
                            attrib={
                                "cx": str(drill_x),
                                "cy": str(drill_y),
                                "r": "0.5",
                                "stroke-width": "0.35",
                                "stroke": "brown",
                                "fill": "none",
                            },
                        )

                else:
                    raise NotImplementedError(component)
        else:
            raise NotImplementedError(component)

    return root
