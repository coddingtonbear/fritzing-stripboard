import datetime
from typing import Any, Protocol, Union, Sequence
import uuid
from xml.etree import ElementTree

from pydantic import BaseModel, Field


CellRangePattern = r"([A-Z]+\d+):([A-Z]+\d+)"


class BoardMetadata(BaseModel):
    id: str = Field(default_factory=uuid.uuid4)

    width: float
    height: float

    version: str = "1.0"
    author: str = "Adam Coddington"

    title: str
    date: datetime.datetime = Field(default_factory=datetime.datetime.utcnow)
    label: str

    properties: dict[str, str] = Field(default_factory=dict)
    taxonomy: str = "prototyping.perfboard.perfboard"
    description: str = (
        "Stripboard generated with "
        "https://github.com/coddingtonbear/fritzing-stripboard"
    )


class GridComponentBaseModel(BaseModel):
    id: str = Field(default_factory=uuid.uuid4)


class XYDrilledBus(GridComponentBaseModel):
    drilled: str = Field(regex=CellRangePattern)


class XYBus(GridComponentBaseModel):
    bus: str = Field(regex=CellRangePattern)


class XYDrilledBusRows(GridComponentBaseModel):
    drilled_rows: str = Field(regex=CellRangePattern)


class XYDrilledBusColumns(GridComponentBaseModel):
    drilled_columns: str = Field(regex=CellRangePattern)


class SharedBus(GridComponentBaseModel):
    shared_bus: Sequence["GridComponent"] = Field(default_factory=list)


GridComponent = Union[
    XYBus, XYDrilledBus, XYDrilledBusColumns, XYDrilledBusRows, SharedBus
]

SharedBus.update_forward_refs()


class GridMetadata(BaseModel):
    origin: tuple[float, float] = (0, 0)
    pitch: float = 2.54


class GridDefinitionData(BaseModel):
    meta: GridMetadata = Field(default_factory=GridMetadata)
    components: Sequence[GridComponent] = Field(default_factory=list)


class GridDefinition(BaseModel):
    grid: GridDefinitionData


BoardComponent = GridDefinition


class BoardSpecification(BaseModel):
    meta: BoardMetadata
    board: list[GridDefinition] = Field(default_factory=list)


class NodeHandler(Protocol):
    def __call__(
        self,
        svg_element: ElementTree.Element,
        connectors_element: ElementTree.Element,
        buses_element: ElementTree.Element,
        config: Any,
        **kwargs
    ) -> None:
        ...
