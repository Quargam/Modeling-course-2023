import dataclasses
from enum import Enum, auto
import typing


SIMPLE_POINT = typing.Tuple[int, int]


class TypeTile(Enum):
    barricade = auto()
    empty = auto()
    unknown = auto()
    robot = auto()
    conveyor = auto()
    storage = auto()


@dataclasses.dataclass()
class Point:
    x: int
    y: int

    @classmethod
    def from_tuple(cls, location):
        return cls(*location)

    def __add__(self, other):
        if isinstance(other, Point):
            return Point(self.x + other.x, self.y + other.y)
        raise TypeError("Unsupported operand type for +")

    def __sub__(self, other):
        if isinstance(other, Point):
            return Point(self.x - other.x, self.y - other.y)
        raise TypeError("Unsupported operand type for -")

    def __str__(self) -> str:
        return f'({self.x:3}, {self.y:3})'


class Direction(Enum):
    UP = Point(0, 1)
    DOWN = Point(0, -1)
    RIGHT = Point(1, 0)
    LEFT = Point(-1, 0)
    HOLDING = Point(0, 0)


@dataclasses.dataclass()
class Tile:
    location_point: Point
    type_tile: TypeTile

    def __str__(self) -> str:
        return f'{self.type_tile.name[0]}'


@dataclasses.dataclass()
class TilesMap:
    """Keyword arguments:
    * size -- map size.
    * tiles_map -- double array of Tiles. All elements of the array have been shifted to the lower left corner.
    """
    size: typing.Tuple[int, int]
    tiles_map: typing.List[typing.List[Tile]]

    def __str__(self) -> str:
        res: typing.List[str] = []
        for line_tiles in self.tiles_map:
            res.append('; '.join(map(str, line_tiles)))
        return '\n'.join(res)

    def is_valid_move(self, point: Point) -> bool:
        """checks only for any objects"""
        return 0 <= point.x < self.size[0] \
            and 0 <= point.y < self.size[1] \
            and self.tiles_map[point.y][point.x].type_tile == TypeTile.empty

    def is_check_block_move(self, point: Point) -> bool:
        """checks only for static objects"""
        return 0 <= point.x < self.size[0] \
            and 0 <= point.y < self.size[1] \
            and (self.tiles_map[point.y][point.x].type_tile == TypeTile.empty
                 or self.tiles_map[point.y][point.x].type_tile == TypeTile.robot)

    def set_type_tile(self, point: Point, type_tile: TypeTile) -> None:
        assert self.is_valid_move(point)
        self.tiles_map[point.y][point.x].type_tile = type_tile

    def reset_type_tile(self, point: Point) -> None:
        self.tiles_map[point.y][point.x].type_tile = TypeTile.empty


@dataclasses.dataclass(frozen=True)
class Line:
    point_start: Point
    point_end: Point

    def __post_init__(self) -> None:
        assert self.point_start.x == self.point_end.x or self.point_start.y == self.point_end.y, \
            'The points must be on the same line, namely vertically or horizontally.'

    def __eq__(self, __value: object) -> bool:
        if not isinstance(__value, 'Line'):
            return False
        return ((self.point_start == __value.point_start and self.point_end == __value.point_end) or
                (self.point_start == __value.point_end and self.point_end == __value.point_start))

    @property
    def points(self) -> typing.List[Point]:
        if self.point_start.x == self.point_end.x:
            start, end = sorted([self.point_start.y, self.point_end.y])
            return [Point(self.point_start.x, y) for y in range(start, end + 1)]
        start, end = sorted([self.point_start.x, self.point_end.x])
        return [Point(x, self.point_start.y) for x in range(start, end + 1)]


def create_tiles_map(
    walls_point: typing.Collection[SIMPLE_POINT],
    other_point: typing.Collection[typing.Union[SIMPLE_POINT, typing.Tuple[SIMPLE_POINT, SIMPLE_POINT]]],
) -> TilesMap:

    def _create_lines(walls_point: typing.Collection[SIMPLE_POINT]) -> typing.Collection[Line]:
        points: typing.List[Point] = [Point(x, y) for x, y in walls_point]
        lines: typing.List[Line] = []
        for ind, point in enumerate(points[:-1]):
            lines.append(Line(point, points[ind+1]))
        lines.append(Line(points[-1], points[0]))
        return lines

    # Moving walls the lower left corner to the origin.
    all_y_val = [y for _, y in walls_point]
    all_x_val = [x for x, _ in walls_point]
    min_x, min_y = min(all_x_val), min(all_y_val)
    max_x, max_y = max(all_x_val), max(all_y_val)

    points: typing.List[Point] = []
    for line in _create_lines(walls_point):
        points.extend(line.points)
    # Сreating a matrix of tiles.
    tiles_map = [[Tile(Point(j, i), TypeTile.empty) for j in range(max_x - min_x + 1)]
                 for i in range(max_y - min_y + 1)]

    for element in other_point:
        if isinstance(element[0], int):
            points.append(Point.from_tuple(element))
        else:
            for line in _create_lines(element):
                points.extend(line.points)

    # Writing a matrix of tiles.
    for point in points:
        x = point.x
        y = point.y
        tiles_map[y - min_y][x - min_x] = Tile(Point(x - min_x, y - min_y), TypeTile.barricade)
    return TilesMap(
            size=(max_x - min_x + 1, max_y - min_y + 1),
            tiles_map=tiles_map,
        )
