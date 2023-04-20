import datetime
from typing import Any, Iterable, Protocol
import uuid
from xml.etree import ElementTree

from pydantic import BaseModel, Field


XYPathPattern = r"([A-Z]+\d+):([A-Z]+\d+)"


class BoardMetadata(BaseModel):
    id: uuid.UUID = Field(default_factory=uuid.uuid4)

    version: str = "1.0"
    author: str = "Adam Coddington"

    title: str
    date: datetime.datetime = Field(default_factory=datetime.datetime.utcnow)
    label: str

    properties: dict[str, str] = Field(default_factory=dict)
    taxonomy: str = "prototyping.perfboard.perfboard"
    description: str = "Stripboard generated with https://github.com/coddingtonbear/fritzing-stripboard"


class XYDrilledBus(BaseModel):
    id: uuid.UUID = Field(default_factory=uuid.uuid4)
    drilled: str = Field(regex=XYPathPattern)


XYGridComponent = XYDrilledBus


class GridDefinitionData(BaseModel):
    origin: tuple[float, float] = (0, 0)
    pitch: float = 2.54
    components: list[XYGridComponent] = Field(default_factory=list)


class GridDefinition(BaseModel):
    grid: GridDefinitionData


BoardComponent = GridDefinition


class BoardSpecification(BaseModel):
    meta: BoardMetadata
    width: float
    height: float
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
