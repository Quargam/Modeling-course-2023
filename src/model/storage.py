import abc
import dataclasses
import typing
import random

import simpy

from .tile import Point, TilesMap, Direction, TypeTile


class BaseModelAgent(abc.ABC):
    @abc.abstractclassmethod
    def run(self, env: simpy.Environment) -> None: ...


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
        direction: Point = Direction.UP,
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

    def __init__(self, id_conveyor: int, location_point: Point, types_mail: typing.Collection[str]) -> None:
        self.id_conveyor = id_conveyor
        self.location_point = location_point
        self.types_mail = types_mail

    def return_package_mail(self) -> MailPackage:
        mail = MailPackage(PackageConveyor._global_id_mail, random.choice(self.types_mail))
        PackageConveyor._global_id_mail += 1
        return mail

    def run(self, env: simpy.Environment) -> None:
        pass


class PackageStorage(BaseModelAgent):
    def __init__(self, id: int, location_point: Point, types_mail: typing.Collection[str]) -> None:
        self.id = id
        self.location_point = location_point
        self.types_mail = types_mail

    def run(self) -> None:
        pass


class StorageSystem(BaseModelAgent):
    def __init__(
        self,
        map_storage: TilesMap,
        package_conveyors: typing.Collection[PackageConveyor],
        package_storages: typing.Collection[PackageStorage],
        robots: typing.Collection[Robot],
        env: simpy.Environment = simpy.Environment(),
    ) -> None:
        self.map_storage = map_storage
        self.package_conveyors = package_conveyors
        self.package_storages = package_storages
        self.robots = robots
        self.env = env

        self.__post_init__()

    def __post_init__(self) -> None:
        for conveyor in self.package_conveyors:
            self.map_storage.set_type_tile(conveyor.location_point, TypeTile.conveyor)
        for storage in self.package_storages:
            self.map_storage.set_type_tile(storage.location_point, TypeTile.storage)
        for robot in self.robots:
            self.map_storage.set_type_tile(robot.location_point, TypeTile.robot)

    def run(self) -> None:
        for robot in self.robots:
            self.env.process(robot.run())
