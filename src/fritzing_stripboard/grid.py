import re
from typing import Iterable

from .types import GridMetadata


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
    grid_meta: GridMetadata,
) -> tuple[float, float]:
    x = coordinate[0]
    y = coordinate[1]
    pitch = grid_meta.pitch
    origin = grid_meta.origin

    x_position = x * pitch + pitch / 2
    y_position = y * pitch + pitch / 2
    if grid_meta.back:
        x_position *= -1

    return origin[0] + x_position, origin[1] + y_position


def get_drill_positions_between_coordinates(
    start: tuple[int, int],
    end: tuple[int, int],
    grid_meta: GridMetadata,
) -> Iterable[tuple[float, float]]:
    start_x, start_y = start
    end_x, end_y = end

    x_offset = min(start_x, end_x)
    y_offset = min(start_y, end_y)
    for x in range(abs(end_x - start_x) + 1):
        for y in range(abs(end_y - start_y) + 1):
            position = convert_coordinate_to_position(
                (x + x_offset, y + y_offset), grid_meta=grid_meta
            )
            yield position
