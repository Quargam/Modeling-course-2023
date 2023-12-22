import typing

from .tile import TilesMap, TypeTile
from .entities import BaseModelAgent, PackageConveyor, PackageStorage, Robot


class StorageSystem(BaseModelAgent):
    def __init__(
        self,
        map_storage: TilesMap,
        package_conveyors: typing.Collection[PackageConveyor],
        package_storages: typing.Collection[PackageStorage],
        robots: typing.Collection[Robot],
    ) -> None:
        self.map_storage = map_storage
        self.package_conveyors = package_conveyors
        self.package_storages = package_storages
        self.robots = robots

        self.__post_init__()

    def __post_init__(self) -> None:
        if PackageConveyor._types_mail != PackageStorage._types_mail:
            raise Exception

        for conveyor in self.package_conveyors:
            self.map_storage.set_type_tile(conveyor.location_point, TypeTile.conveyor)
        for storage in self.package_storages:
            self.map_storage.set_type_tile(storage.location_point, TypeTile.storage)
        for robot in self.robots:
            self.map_storage.set_type_tile(robot.location_point, TypeTile.robot)
