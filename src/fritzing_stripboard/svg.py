from typing import Iterable, Type
from xml.etree import ElementTree

from pydantic import BaseModel

from .types import (
    BoardSpecification,
    GridDefinition,
    GridDefinitionData,
    XYDrilledBus,
    NodeHandler,
)
from .grid import (
    InvalidCellRange,
    convert_cell_to_coordinate,
    convert_coordinate_to_position,
    get_drill_positions_in_cell_range,
)


class NodeTypeNotImplemented(Exception):
    pass


def get_handler(component: BaseModel) -> NodeHandler:
    handlers: dict[Type[BaseModel], NodeHandler] = {
        GridDefinition: handle_grid_definition,
        XYDrilledBus: handle_xy_drilled_bus,
    }

    try:
        return handlers[type(component)]
    except IndexError as exc:
        raise NodeTypeNotImplemented(component) from exc


def handle_xy_drilled_bus(
    g: ElementTree.Element,
    envelope: XYDrilledBus,
    **kwargs,
) -> Iterable[ElementTree.Element]:
    item = envelope
    grid: GridDefinitionData = kwargs["grid"]

    start, end = item.drilled.split(":")

    start_x, start_y = convert_coordinate_to_position(
        convert_cell_to_coordinate(start),
        origin=grid.origin,
        pitch=grid.pitch,
    )
    end_x, end_y = convert_coordinate_to_position(
        convert_cell_to_coordinate(end),
        origin=grid.origin,
        pitch=grid.pitch,
    )

    if not (start_x == end_x or end_y == start_y):
        raise InvalidCellRange(item.drilled)

    yield ElementTree.SubElement(
        g,
        "line",
        attrib={
            "x1": f"{start_x}mm",
            "y1": f"{start_y}mm",
            "x2": f"{end_x}mm",
            "y2": f"{end_y}mm",
            "stroke": "brown",
            "stroke-width": "1.5mm",
            "style": "stroke-linecap:round; stroke-opacity: 0.5;",
        },
    )

    for drill_x, drill_y in get_drill_positions_in_cell_range(
        start,
        end,
        origin=grid.origin,
        pitch=grid.pitch,
    ):
        yield ElementTree.SubElement(
            g,
            "circle",
            attrib={
                "cx": f"{drill_x}mm",
                "cy": f"{drill_y}mm",
                "r": "0.5mm",
                "stroke-width": "0.35mm",
                "stroke": "brown",
                "fill": "none",
            },
        )


def handle_grid_definition(
    g: ElementTree.Element, envelope: GridDefinition, **kwargs
) -> Iterable[ElementTree.Element]:
    grid = envelope.grid

    for item in grid.components:
        handler = get_handler(item)
        list(handler(g, item, grid=grid))

    return []


def build_svg(board: BoardSpecification) -> ElementTree.Element:
    root = ElementTree.Element(
        "svg",
        attrib={
            "width": f"{board.width}mm",
            "height": f"{board.height}mm",
            "viewbox": f"0 0 {board.width}mm {board.height}mm",
        },
    )
    g = ElementTree.SubElement(root, "g", attrib={"id": "breadboard"})

    ElementTree.SubElement(
        g,
        "path",
        attrib={
            "transform": "scale(35433)",
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
        handler = get_handler(component)
        list(handler(g, component))

    return root
