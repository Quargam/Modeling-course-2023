import abc
import dataclasses
from enum import Enum
import typing
import random

import simpy


class BaseModelAgent(abc.ABC):
    @abc.abstractclassmethod
    def run(self, env: simpy.Environment) -> None: ...


@dataclasses.dataclass(frozen=True)
class Point:
    x: int
    y: int


class Direction(Enum):
    UP = Point(0, 1)
    DOWN = Point(0, -1)
    RIGHT = Point(1, 0)
    LEFT = Point(-1, 0)


@dataclasses.dataclass(frozen=True)
class Wall:
    point_start: Point
    point_end: Point

    def __post_init__(self) -> None:
        assert self.point_start.x == self.point_end.x or self.point_start.y == self.point_end.y, \
            'Точки стены должны находиться на одной линии, а именно вертикально или горизонтально.'

    def __eq__(self, __value: object) -> bool:
        if not isinstance(__value, 'Wall'):
            return False
        return ((self.point_start == __value.point_start and self.point_end == __value.point_end) or
                (self.point_start == __value.point_end and self.point_end == __value.point_start))

    def check_collision_point(self, point: Point) -> bool:
        if self.point_start.x == point.x and (self.point_start.y <= point.y <= self.point_end.y or
                                              self.point_end.y <= point.y <= self.point_start.y):
            return True
        if self.point_start.y == point.y and (self.point_start.x <= point.x <= self.point_end.x or
                                              self.point_end.x <= point.x <= self.point_start.x):
            return True
        return False


@dataclasses.dataclass()
class WallsStorage(BaseModelAgent):
    walls: typing.Collection[Wall]

    def check_collision_wall(self, point: Point) -> bool:
        for wall in self.walls:
            if wall.check_collision_point(point):
                return True
        return False

    def run(self, env: simpy.Environment) -> None:
        pass


def create_walls_storage(val_point: typing.Collection[typing.Tuple[int, int]]) -> WallsStorage:
    points: typing.List[Point] = [Point(x, y) for x, y in val_point]
    walls: typing.List[Wall] = []
    for ind, point in enumerate(points[:-1]):
        walls.append(Wall(point, points[ind+1]))
    walls.append(Wall(points[-1], points[0]))
    return WallsStorage(walls)


@dataclasses.dataclass(frozen=True)
class MailPackage:
    id: int
    type_mail: str
    message: str = dataclasses.field(default='')


class Robot(BaseModelAgent):
    def __init__(
        self,
        id: int,
        location_point: Point,
        direction: Point,
        package_mail: typing.Optional[MailPackage] = None
    ) -> None:
        self.id = id
        self.location_point = location_point
        self.direction = direction
        self.package_mail = package_mail

    def move_forward(self) -> None:
        self.location_point += self.direction

    def backward(self) -> None:
        self.location_point -= self.direction

    def turn_left(self) -> None:
        self.direction = Point(self.direction.y * -1, self.direction.x)

    def right_left(self) -> None:
        self.direction = Point(self.direction.y, self.direction.x * -1)

    def stand_here(self) -> None:
        pass

    def take_package(self, mail: MailPackage) -> None:
        assert not self.package_mail, 'The robot has a package.'
        self.package_mail = mail

    def give_package(self) -> MailPackage:
        assert self.package_mail, 'The robot does not have a package.'
        mail = self.package_mail
        self.package_mail = None
        return mail

    def run(self, env: simpy.Environment) -> None:
        pass


class PackageConveyor(BaseModelAgent):
    _global_id_mail = 0

    def __init__(self, id: int, location_point: Point, types_mail: typing.Collection[str]) -> None:
        self.id = id
        self.location_point = location_point
        self.types_mail = types_mail

    def return_package_mail(self) -> MailPackage:
        mail = MailPackage(PackageConveyor._global_id_mail, random.choice(self.types_mail))
        PackageConveyor._global_id_mail += 1
        return mail

    def run(self, env: simpy.Environment) -> None:
        pass


class PackageStorage(BaseModelAgent):
    def __init__(self, id: int, location_point: Point) -> None:
        self.id = id
        self.location_point = location_point

    def run(self) -> None:
        pass


class StorageSystem(BaseModelAgent):
    def __init__(
        self,
        walls_storage: WallsStorage,
        package_conveyors: typing.Collection[PackageConveyor],
        package_storages: typing.Collection[PackageStorage],
        robots: typing.Collection[Robot],
        env: simpy.Environment = simpy.Environment(),
    ) -> None:
        self.walls_storage = walls_storage
        self.package_conveyors = package_conveyors
        self.package_storages = package_storages
        self.robots = robots
        self.env = env

    def run(self) -> None:
        for robot in self.robots:
            self.env.process(robot.run())
