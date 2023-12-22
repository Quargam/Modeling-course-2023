import abc
import dataclasses
import typing
import random
import csv

from .tile import TilesMap, Point, Direction, TypeTile
from .storage import StorageSystem, Robot, PackageConveyor, PackageStorage


class ControllerStorageSys(abc.ABC):
    @abc.abstractmethod
    def check_taking_pack(self, robot: Robot) -> typing.Optional[PackageConveyor]: ...

    @abc.abstractmethod
    def check_giving_pack(self, robot: Robot) -> typing.Optional[PackageStorage]: ...


@dataclasses.dataclass()
class _pheromon_tile:
    point: Point
    up_pher: typing.Optional[float] = None
    down_pher: typing.Optional[float] = None
    left_pher: typing.Optional[float] = None
    right_pher: typing.Optional[float] = None
    holding_pher: typing.Optional[float] = None

    def del_pheromon(self, coef: float = 0.7) -> None:
        if self.up_pher:
            self.up_pher *= coef
        if self.down_pher:
            self.down_pher *= coef
        if self.left_pher:
            self.left_pher *= coef
        if self.right_pher:
            self.right_pher *= coef
        if self.holding_pher:
            self.holding_pher *= coef

    def add_pheramon(self, direction: Point, correction_pher: float) -> None:
        if direction == Direction.UP.value:
            self.up_pher += correction_pher
        if direction == Direction.DOWN.value:
            self.down_pher += correction_pher
        if direction == Direction.LEFT.value:
            self.left_pher += correction_pher
        if direction == Direction.RIGHT.value:
            self.right_pher += correction_pher
        if direction == Direction.HOLDING.value:
            self.holding_pher += correction_pher

    def return_direction_move(self, ignore_dir=[]) -> Point:
        dir: typing.List[Point] = []
        expectation: typing.List[float] = []
        if self.up_pher and Direction.UP.value not in ignore_dir:
            dir.append(Direction.UP.value)
            expectation.append(self.up_pher)
        if self.down_pher and Direction.DOWN.value not in ignore_dir:
            dir.append(Direction.DOWN.value)
            expectation.append(self.down_pher)
        if self.left_pher and Direction.LEFT.value not in ignore_dir:
            dir.append(Direction.LEFT.value)
            expectation.append(self.left_pher)
        if self.right_pher and Direction.RIGHT.value not in ignore_dir:
            dir.append(Direction.RIGHT.value)
            expectation.append(self.right_pher)
        if self.holding_pher:
            dir.append(Direction.HOLDING.value)
            expectation.append(self.holding_pher)
        return random.choices(dir, weights=expectation)[0]


@dataclasses.dataclass()
class _Pheromon_map:
    size: typing.Tuple[int, int]
    tiles_map: typing.List[typing.List[_pheromon_tile]]

    def del_pheromon(self) -> None:
        for lane_tiles in self.tiles_map:
            for tile in lane_tiles:
                tile.del_pheromon()

    def return_tile(self, point: Point) -> _pheromon_tile:
        return self.tiles_map[point.y][point.x]


def create_pheromon_map(map_storage: TilesMap) -> _Pheromon_map:
    pher_map = [[_pheromon_tile(Point(j, i)) for j in range(map_storage.size[0])] for i in range(map_storage.size[1])]
    for x in range(map_storage.size[0]):
        for y in range(map_storage.size[1]):
            point = Point(x, y)
            if not map_storage.is_check_block_move(point + Direction.HOLDING.value):
                continue
            if map_storage.is_check_block_move(point + Direction.UP.value):
                pher_map[y][x].up_pher = 1
            if map_storage.is_check_block_move(point + Direction.DOWN.value):
                pher_map[y][x].down_pher = 1
            if map_storage.is_check_block_move(point + Direction.LEFT.value):
                pher_map[y][x].left_pher = 1
            if map_storage.is_check_block_move(point + Direction.RIGHT.value):
                pher_map[y][x].right_pher = 1
            pher_map[y][x].holding_pher = 1
    return _Pheromon_map(map_storage.size, pher_map)


class AntControllerStorageSys(ControllerStorageSys):
    def __init__(
        self,
        storage_system: StorageSystem,
        max_package: int,
        log_file: typing.TextIO,
    ) -> None:
        self.storage_system = storage_system
        self.max_package = max_package
        self.log_file = log_file

    def __post_init__(self) -> None:
        pass

    def check_taking_pack(self, robot: Robot) -> typing.Optional[PackageConveyor]:
        for conveyor in self.storage_system.package_conveyors:
            if conveyor.out_point:
                if conveyor.out_point == robot.location_point:
                    return conveyor
                else:
                    return False
            if robot.location_point == conveyor.location_point + Direction.UP.value:
                return conveyor
            if robot.location_point == conveyor.location_point + Direction.DOWN.value:
                return conveyor
            if robot.location_point == conveyor.location_point + Direction.LEFT.value:
                return conveyor
            if robot.location_point == conveyor.location_point + Direction.RIGHT.value:
                return conveyor
            return False

    def check_giving_pack(self, robot: Robot) -> typing.Optional[PackageStorage]:
        for storage in self.storage_system.package_storages:
            if robot.package_mail.type_mail not in storage.types_mail:
                continue
            if robot.location_point == storage.location_point + Direction.UP.value:
                return storage
            if robot.location_point == storage.location_point + Direction.DOWN.value:
                return storage
            if robot.location_point == storage.location_point + Direction.LEFT.value:
                return storage
            if robot.location_point == storage.location_point + Direction.RIGHT.value:
                return storage
        return False

    def run(self) -> None:

        def travel_descent(
            travel: typing.List[Point],
            point: Point,
            pher_map: _Pheromon_map,
        ) -> None:
            loc_point = point
            for direction in travel[::-1]:
                if direction == Point(0, 0):
                    continue
                loc_point -= direction
                tile = pher_map.return_tile(loc_point)
                tile.add_pheramon(direction, 1 / len(travel))
                pher_map.tiles_map[loc_point.y][loc_point.x] = tile

        fieldnames = ['time', 'id_action', 'id_robot', 'point', 'point_target', 'desc']
        writer = csv.DictWriter(self.log_file, fieldnames=fieldnames)
        writer.writeheader()

        time = 0
        count_package = 0

        pher_map_mail: typing.Dict[str, _Pheromon_map] = {}
        for type_mail in PackageStorage._types_mail:
            pher_map_mail[type_mail] = create_pheromon_map(self.storage_system.map_storage)
        pher_map_mail_all: _Pheromon_map = create_pheromon_map(self.storage_system.map_storage)
        rob_travel: typing.Dict[int, typing.List[Direction]] = {}
        for robot in self.storage_system.robots:
            rob_travel[robot.id] = []

        while count_package <= self.max_package:
            for robot in self.storage_system.robots:
                log_command: dict = {
                    'time': time, 'id_action': 0, 'id_robot': 0, 'point': (0, 0), 'point_target': (0, 0), 'desc': '-',
                }

                if robot.package_mail:
                    pher_map = pher_map_mail[robot.package_mail.type_mail]
                else:
                    pher_map = pher_map_mail_all

                if robot.package_mail:
                    if storage := self.check_giving_pack(robot):
                        mail = robot.package_mail
                        log_command['id_action'] = 0
                        log_command['id_robot'] = robot.id
                        log_command['point'] = (robot.location_point.x, robot.location_point.y)
                        log_command['point_target'] = (storage.location_point.x, storage.location_point.y)
                        log_command['desc'] = \
                            f'put mail type {robot.package_mail.type_mail} with index {robot.package_mail.id}'
                        writer.writerow(log_command)
                        robot.package_mail = None

                        if count_package % 100 == 0:
                            print(count_package)
                        count_package += 1

                        travel = rob_travel[robot.id]
                        pher_map_mail[mail.type_mail].del_pheromon()
                        travel_descent(travel, robot.location_point, pher_map)
                        rob_travel[robot.id] = []
                        continue
                else:
                    if conveyor := self.check_taking_pack(robot):
                        robot.package_mail = conveyor.return_package_mail()
                        travel = rob_travel[robot.id]
                        pher_map_mail_all.del_pheromon()
                        travel_descent(travel, robot.location_point, pher_map)
                        rob_travel[robot.id] = []
                        log_command['id_action'] = 1
                        log_command['id_robot'] = robot.id
                        log_command['point'] = (robot.location_point.x, robot.location_point.y)
                        log_command['point_target'] = (conveyor.location_point.x, conveyor.location_point.y)
                        log_command['desc'] = \
                            f'take mail type {robot.package_mail.type_mail} with index {robot.package_mail.id}'
                        writer.writerow(log_command)
                        continue

                ignore_dir = []
                while True:
                    move_direction = pher_map.return_tile(robot.location_point).return_direction_move(ignore_dir)
                    if (self.storage_system.map_storage.is_valid_move(robot.location_point + move_direction)
                            or move_direction == Point(0, 0)):

                        end_point = robot.location_point + move_direction
                        log_command['id_action'] = 2
                        log_command['id_robot'] = robot.id
                        log_command['point'] = (robot.location_point.x, robot.location_point.y)
                        log_command['point_target'] = (end_point.x, end_point.y)
                        if robot.package_mail:
                            log_command['desc'] = \
                                f'move mail type {robot.package_mail.type_mail} with index {robot.package_mail.id}'
                        else:
                            log_command['desc'] = 'move without mail'
                        writer.writerow(log_command)
                        self.storage_system.map_storage.reset_type_tile(robot.location_point)
                        robot.location_point += move_direction
                        self.storage_system.map_storage.set_type_tile(robot.location_point, TypeTile.robot)
                        ignore_dir = []
                        break
                    else:
                        ignore_dir.append(move_direction)
                rob_travel[robot.id].append(move_direction)
            time += 1
