from xml.etree import ElementTree
from typing import Type
import zipfile

from pydantic import BaseModel

from .grid import (
    InvalidCellRange,
    convert_cell_to_coordinate,
    convert_coordinate_to_position,
    get_drill_positions_between_coordinates,
)
from .types import (
    BoardSpecification,
    NodeHandler,
    GridDefinition,
    SharedBus,
    XYBus,
    XYDrilledBus,
    XYDrilledBusColumns,
    XYDrilledBusRows,
    GridDefinitionData,
)


HANDLER_REGISTRY: dict[Type[BaseModel], NodeHandler] = {}


class NodeTypeNotImplemented(Exception):
    pass


def get_handler(component: BaseModel) -> NodeHandler:
    handlers: dict[Type[BaseModel], NodeHandler] = {
        GridDefinition: handle_grid_definition,
        XYDrilledBus: handle_xy_drilled_bus,
        XYDrilledBusColumns: handle_xy_drilled_bus_columns,
        XYDrilledBusRows: handle_xy_drilled_bus_rows,
        XYBus: handle_xy_bus,
        SharedBus: handle_shared_bus,
    }

    try:
        return handlers[type(component)]
    except KeyError as exc:
        raise NodeTypeNotImplemented(component) from exc


def handle_shared_bus(
    svg_element: ElementTree.Element,
    connectors_element: ElementTree.Element,
    buses_element: ElementTree.Element,
    config: SharedBus,
    **kwargs,
) -> None:
    bus = kwargs.get(
        "bus",
        ElementTree.SubElement(buses_element, "bus", attrib={"id": str(config.id)}),
    )

    for item in config.shared_bus:
        handler = get_handler(item)
        handler(svg_element, connectors_element, buses_element, item, bus=bus, **kwargs)


def handle_xy_drilled_bus_rows(
    svg_element: ElementTree.Element,
    connectors_element: ElementTree.Element,
    buses_element: ElementTree.Element,
    config: XYDrilledBusRows,
    **kwargs,
) -> None:
    item = config
    grid: GridDefinitionData = kwargs["grid"]

    start, end = item.drilled_rows.split(":")

    start_coord_x, start_coord_y = convert_cell_to_coordinate(start)
    end_coord_x, end_coord_y = convert_cell_to_coordinate(end)

    y_offset = min(start_coord_y, end_coord_y)
    for y in range(abs(end_coord_y - start_coord_y) + 1):
        bus = kwargs.get(
            "bus",
            ElementTree.SubElement(
                buses_element, "bus", attrib={"id": f"{item.id}-{y}"}
            ),
        )

        line_start_position = convert_coordinate_to_position(
            (start_coord_x, y + y_offset), origin=grid.origin, pitch=grid.pitch
        )
        line_end_position = convert_coordinate_to_position(
            (end_coord_x, y + y_offset), origin=grid.origin, pitch=grid.pitch
        )
        line_connector_id = f"{item.id}-{y}-trace"
        ElementTree.SubElement(
            svg_element,
            "line",
            attrib={
                "id": line_connector_id,
                "x1": f"{line_start_position[0]}mm",
                "y1": f"{line_start_position[1]}mm",
                "x2": f"{line_end_position[0]}mm",
                "y2": f"{line_end_position[1]}mm",
                "stroke": "brown",
                "stroke-width": "1.5mm",
                "style": "stroke-linecap:round; stroke-opacity: 0.5;",
            },
        )

        for idx, (drill_x, drill_y) in enumerate(
            get_drill_positions_between_coordinates(
                (start_coord_x, y + y_offset),
                (end_coord_x, y + y_offset),
                origin=grid.origin,
                pitch=grid.pitch,
            )
        ):
            connector_id = f"{item.id}-{y}-{idx}"

            ElementTree.SubElement(
                svg_element,
                "circle",
                attrib={
                    "id": connector_id,
                    "cx": f"{drill_x}mm",
                    "cy": f"{drill_y}mm",
                    "r": "0.5mm",
                    "stroke-width": "0.35mm",
                    "stroke": "brown",
                    "fill": "none",
                },
            )

            ElementTree.SubElement(
                bus,
                "nodeMember",
                attrib={"connectorId": connector_id},
            )

            connector = ElementTree.SubElement(
                connectors_element,
                "connector",
                attrib={
                    "type": "female",
                    "name": connector_id,
                    "id": connector_id,
                },
            )
            connector_views = ElementTree.SubElement(connector, "views")
            connector_breadboard_view = ElementTree.SubElement(
                connector_views, "breadboardView"
            )
            ElementTree.SubElement(
                connector_breadboard_view,
                "p",
                attrib={"layer": "breadboard", "svgId": connector_id},
            )


def handle_xy_drilled_bus_columns(
    svg_element: ElementTree.Element,
    connectors_element: ElementTree.Element,
    buses_element: ElementTree.Element,
    config: XYDrilledBusColumns,
    **kwargs,
) -> None:
    item = config
    grid: GridDefinitionData = kwargs["grid"]

    start, end = item.drilled_columns.split(":")

    start_coord_x, start_coord_y = convert_cell_to_coordinate(start)
    end_coord_x, end_coord_y = convert_cell_to_coordinate(end)

    x_offset = min(start_coord_x, end_coord_x)
    for x in range(abs(end_coord_x - start_coord_x) + 1):
        bus = kwargs.get(
            "bus",
            ElementTree.SubElement(
                buses_element, "bus", attrib={"id": f"{item.id}-{x}"}
            ),
        )

        line_start_position = convert_coordinate_to_position(
            (x + x_offset, start_coord_y), origin=grid.origin, pitch=grid.pitch
        )
        line_end_position = convert_coordinate_to_position(
            (x + x_offset, end_coord_y), origin=grid.origin, pitch=grid.pitch
        )
        line_connector_id = f"{item.id}-{x}-trace"
        ElementTree.SubElement(
            svg_element,
            "line",
            attrib={
                "id": line_connector_id,
                "x1": f"{line_start_position[0]}mm",
                "y1": f"{line_start_position[1]}mm",
                "x2": f"{line_end_position[0]}mm",
                "y2": f"{line_end_position[1]}mm",
                "stroke": "brown",
                "stroke-width": "1.5mm",
                "style": "stroke-linecap:round; stroke-opacity: 0.5;",
            },
        )

        for idx, (drill_x, drill_y) in enumerate(
            get_drill_positions_between_coordinates(
                (x + x_offset, start_coord_y),
                (x + x_offset, end_coord_y),
                origin=grid.origin,
                pitch=grid.pitch,
            )
        ):
            connector_id = f"{item.id}-{x}-{idx}"

            ElementTree.SubElement(
                svg_element,
                "circle",
                attrib={
                    "id": connector_id,
                    "cx": f"{drill_x}mm",
                    "cy": f"{drill_y}mm",
                    "r": "0.5mm",
                    "stroke-width": "0.35mm",
                    "stroke": "brown",
                    "fill": "none",
                },
            )

            connector_id = f"{item.id}-{idx}"
            ElementTree.SubElement(
                bus,
                "nodeMember",
                attrib={"connectorId": connector_id},
            )

            connector = ElementTree.SubElement(
                connectors_element,
                "connector",
                attrib={
                    "type": "female",
                    "name": connector_id,
                    "id": connector_id,
                },
            )
            connector_views = ElementTree.SubElement(connector, "views")
            connector_breadboard_view = ElementTree.SubElement(
                connector_views, "breadboardView"
            )
            ElementTree.SubElement(
                connector_breadboard_view,
                "p",
                attrib={"layer": "breadboard", "svgId": connector_id},
            )


def handle_xy_bus(
    svg_element: ElementTree.Element,
    connectors_element: ElementTree.Element,
    buses_element: ElementTree.Element,
    config: XYBus,
    **kwargs,
) -> None:
    handle_xy_drilled_bus(
        svg_element, connectors_element, buses_element, config, drilled=False, **kwargs
    )


def handle_xy_drilled_bus(
    svg_element: ElementTree.Element,
    connectors_element: ElementTree.Element,
    buses_element: ElementTree.Element,
    config: XYDrilledBus | XYBus,
    **kwargs,
) -> None:
    item = config

    if isinstance(config, XYDrilledBus):
        cell_range = config.drilled
    elif isinstance(config, XYBus):
        cell_range = config.bus
    else:
        raise NotImplementedError(config)

    grid: GridDefinitionData = kwargs["grid"]
    drilled: bool = kwargs.get("drilled", True)

    start, end = cell_range.split(":")

    start_coord_x, start_coord_y = convert_cell_to_coordinate(start)
    end_coord_x, end_coord_y = convert_cell_to_coordinate(end)
    start_x, start_y = convert_coordinate_to_position(
        (start_coord_x, start_coord_y),
        origin=grid.origin,
        pitch=grid.pitch,
    )
    end_x, end_y = convert_coordinate_to_position(
        (end_coord_x, end_coord_y),
        origin=grid.origin,
        pitch=grid.pitch,
    )

    if not (start_x == end_x or end_y == start_y):
        raise InvalidCellRange(cell_range)

    bus = kwargs.get(
        "bus", ElementTree.SubElement(buses_element, "bus", attrib={"id": str(item.id)})
    )

    line_connector_id = f"{item.id}-trace"
    ElementTree.SubElement(
        svg_element,
        "line",
        attrib={
            "id": line_connector_id,
            "x1": f"{start_x}mm",
            "y1": f"{start_y}mm",
            "x2": f"{end_x}mm",
            "y2": f"{end_y}mm",
            "stroke": "brown",
            "stroke-width": "1.5mm",
            "style": "stroke-linecap:round; stroke-opacity: 0.5;",
        },
    )

    for idx, (drill_x, drill_y) in enumerate(
        get_drill_positions_between_coordinates(
            (start_coord_x, start_coord_y),
            (end_coord_x, end_coord_y),
            origin=grid.origin,
            pitch=grid.pitch,
        )
    ):
        connector_id = f"{item.id}-{idx}"

        ElementTree.SubElement(
            svg_element,
            "circle",
            attrib={
                "id": connector_id,
                "cx": f"{drill_x}mm",
                "cy": f"{drill_y}mm",
                "r": "0.5mm" if drilled else "0.1mm",
                "stroke-width": "0.35mm" if drilled else "0.1mm",
                "stroke": "brown",
                "fill": "none",
            },
        )

        ElementTree.SubElement(
            bus,
            "nodeMember",
            attrib={"connectorId": connector_id},
        )

        connector = ElementTree.SubElement(
            connectors_element,
            "connector",
            attrib={
                "type": "female" if drilled else "pad",
                "name": connector_id,
                "id": connector_id,
            },
        )
        connector_views = ElementTree.SubElement(connector, "views")
        connector_breadboard_view = ElementTree.SubElement(
            connector_views, "breadboardView"
        )
        ElementTree.SubElement(
            connector_breadboard_view,
            "p",
            attrib={"layer": "breadboard", "svgId": connector_id},
        )


def handle_grid_definition(
    svg_element: ElementTree.Element,
    connectors_element: ElementTree.Element,
    buses_element: ElementTree.Element,
    config: GridDefinition,
    **kwargs,
) -> None:
    grid = config.grid

    for item in grid.components:
        handler = get_handler(item)
        handler(svg_element, connectors_element, buses_element, item, grid=grid)


def build_part_files(
    board: BoardSpecification,
) -> tuple[ElementTree.Element, ElementTree.Element]:
    svg_root = ElementTree.Element(
        "svg",
        attrib={
            "width": f"{board.width}mm",
            "height": f"{board.height}mm",
            "viewBox": f"0 0 {board.width} {board.height}",
        },
    )
    g = ElementTree.SubElement(svg_root, "g", attrib={"id": "breadboard"})
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

    part_root = ElementTree.Element("module", attrib={"moduleId": str(board.meta.id)})
    ElementTree.SubElement(part_root, "version").text = board.meta.version
    ElementTree.SubElement(part_root, "author").text = board.meta.author
    ElementTree.SubElement(part_root, "title").text = board.meta.title
    ElementTree.SubElement(part_root, "date").text = board.meta.date.isoformat()
    ElementTree.SubElement(part_root, "label").text = board.meta.label
    ElementTree.SubElement(part_root, "tags")

    properties = ElementTree.SubElement(part_root, "properties")
    ElementTree.SubElement(
        properties,
        "property",
        attrib={"name": "size"},
    ).text = f"{board.width}mm X {board.height}mm"
    ElementTree.SubElement(
        properties, "property", attrib={"name": "family"}
    ).text = "Generic Stripboard"

    ElementTree.SubElement(part_root, "taxonomy").text = board.meta.taxonomy
    ElementTree.SubElement(part_root, "description").text = board.meta.description

    views = ElementTree.SubElement(part_root, "views")

    icon_view = ElementTree.SubElement(views, "iconView")
    layers = ElementTree.SubElement(
        icon_view, "layers", attrib={"image": f"breadboard/{board.meta.id}.svg"}
    )
    ElementTree.SubElement(layers, "layer", attrib={"layerId": "icon"})

    breadboard_view = ElementTree.SubElement(views, "breadboardView")
    layers = ElementTree.SubElement(
        breadboard_view, "layers", attrib={"image": f"breadboard/{board.meta.id}.svg"}
    )
    ElementTree.SubElement(layers, "layer", attrib={"layerId": "breadboard"})

    schematic_view = ElementTree.SubElement(views, "schematicView")
    layers = ElementTree.SubElement(
        schematic_view, "layers", attrib={"image": f"breadboard/{board.meta.id}.svg"}
    )
    ElementTree.SubElement(layers, "layer", attrib={"layerId": "schematic"})

    pcb_view = ElementTree.SubElement(views, "pcbView")
    layers = ElementTree.SubElement(
        pcb_view, "layers", attrib={"image": f"breadboard/{board.meta.id}.svg"}
    )
    ElementTree.SubElement(layers, "layer", attrib={"layerId": "pcb"})

    connectors = ElementTree.SubElement(part_root, "connectors")
    buses = ElementTree.SubElement(part_root, "buses")

    for component in board.board:
        handler = get_handler(component)

        handler(g, connectors, buses, component)

    return part_root, svg_root


def build_zip(board: BoardSpecification, path: str) -> None:
    fzp_document, svg_document = build_part_files(board)

    archive = zipfile.ZipFile(path, mode="w")
    with archive.open(f"part.{board.meta.id}.fzp", "w") as fzpf:
        fzpf.write(ElementTree.tostring(fzp_document))

    with archive.open(f"svg.breadboard.{board.meta.id}.svg", "w") as svgf:
        svgf.write(ElementTree.tostring(svg_document))
