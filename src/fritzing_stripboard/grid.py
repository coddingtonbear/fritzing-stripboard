import re
from typing import Iterable


from .constants import DEFAULT_PITCH


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


def get_drill_positions_between_coordinates(
    start: tuple[int, int],
    end: tuple[int, int],
    origin: tuple[float, float] = (0, 0),
    pitch: float = DEFAULT_PITCH,
) -> Iterable[tuple[float, float]]:
    start_x, start_y = start
    end_x, end_y = end

    x_offset = min(start_x, end_x)
    y_offset = min(start_y, end_y)
    for x in range(abs(end_x - start_x) + 1):
        for y in range(abs(end_y - start_y) + 1):
            position = convert_coordinate_to_position(
                (x + x_offset, y + y_offset), origin=origin, pitch=pitch
            )
            yield position
