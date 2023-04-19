from xml.etree import ElementTree

from .types import BoardSpecification, GridDefinition, XYDrilledBus
from .grid import get_drill_positions_in_cell_range


def build_fzp(board: BoardSpecification) -> ElementTree.Element:
    root = ElementTree.Element("module", attrib={"moduleId": board.meta.title})

    ElementTree.SubElement(root, "version", text=board.meta.version)
    ElementTree.SubElement(root, "author", text=board.meta.author)
    ElementTree.SubElement(root, "title", text=board.meta.title)
    ElementTree.SubElement(root, "date", text=board.meta.date.isoformat())
    ElementTree.SubElement(root, "label", text=board.meta.label)
    ElementTree.SubElement(root, "tags")

    properties = ElementTree.SubElement(root, "properties")
    ElementTree.SubElement(
        properties,
        "property",
        attrib={"name": "size"},
        text=f"{board.width}mm X {board.height}mm",
    )
    ElementTree.SubElement(
        properties, "property", attrib={"name": "family"}, text="Generic Stripboard"
    )

    ElementTree.SubElement(root, "taxonomy", text=board.meta.taxonomy)
    ElementTree.SubElement(root, "description", text=board.meta.description)

    views = ElementTree.SubElement(root, "views")

    icon_view = ElementTree.SubElement(views, "iconView")
    layers = ElementTree.SubElement(
        icon_view, "layers", attrib={"image": "breadboard/main.svg"}
    )
    ElementTree.SubElement(layers, "layer", attrib={"layerId": "icon/"})

    breadboard_view = ElementTree.SubElement(views, "breadboardView")
    layers = ElementTree.SubElement(
        breadboard_view, "layers", attrib={"image": "breadboard/main.svg"}
    )
    ElementTree.SubElement(layers, "layer", attrib={"layerId": "breadboard/"})

    schematic_view = ElementTree.SubElement(views, "schematicView")
    layers = ElementTree.SubElement(
        schematic_view, "layers", attrib={"image": "breadboard/main.svg"}
    )
    ElementTree.SubElement(layers, "layer", attrib={"layerId": "schematic/"})

    pcb_view = ElementTree.SubElement(views, "pcbView")
    layers = ElementTree.SubElement(
        pcb_view, "layers", attrib={"image": "breadboard/main.svg"}
    )
    ElementTree.SubElement(layers, "layer", attrib={"layerId": "pcb/"})

    connectors = ElementTree.SubElement(root, "connectors")
    buses = ElementTree.SubElement(root, "buses")

    for component in board.board:
        if isinstance(component, GridDefinition):
            grid = component.grid

            for item in grid.components:
                if isinstance(item, XYDrilledBus):
                    start, end = item.drilled.split(":")

                    bus = ElementTree.SubElement(
                        buses, "bus", attrib={"id": str(item.id)}
                    )

                    for idx, _ in enumerate(
                        get_drill_positions_in_cell_range(
                            start, end, origin=grid.origin, pitch=grid.pitch
                        )
                    ):
                        connector_id = f"{item.id}-{idx}"
                        ElementTree.SubElement(
                            bus,
                            "nodeMember",
                            attrib={"connectorId": connector_id},
                        )

                        connector = ElementTree.SubElement(
                            connectors,
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

                else:
                    raise NotImplementedError(item)
        else:
            raise NotImplementedError(component)

    return root
