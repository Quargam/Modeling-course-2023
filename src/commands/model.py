import argparse
from pathlib import Path
import typing

import yaml

from src.model.tile import create_tiles_map, Point
from src.model.storage import StorageSystem, Robot, PackageConveyor, PackageStorage
from src.model.control import AntControllerStorageSys


class CommandArgument(typing.Protocol):
    args: Path
    log_file: Path


def parse_arguments(arg_parser: argparse.ArgumentParser) -> None:
    arg_parser.add_argument(
        '--log-file',
        dest='log_file',
        metavar='PARAM.csv',
        type=Path,
    )
    arg_parser.add_argument(
        dest='args',
        metavar='PARAM.yaml',
        type=Path,
    )
    arg_parser.set_defaults(command=exec_command)


def exec_command(args: CommandArgument) -> None:
    with open(args.args, 'r') as stream:
        data: dict = yaml.safe_load(stream)
    map_storage = create_tiles_map(data['shape']['walls'], data['shape']['points'])

    robots: typing.List[Robot] = list()
    for ind, locations in enumerate(data['robot']['locations']):
        robots.append(Robot(ind, Point.from_tuple(locations)))

    package_conveyors: typing.List[PackageConveyor] = list()
    for ind, conveyors in enumerate(data['package_conveyors']):
        out_point: typing.Optional(typing.Tuple[int, int]) = conveyors.get('out_point', None)
        package_conveyors.append(
            PackageConveyor(
                ind,
                Point.from_tuple(conveyors['locations']),
                conveyors['types'],
                conveyors.get('expectation', []),
                Point(out_point[0], out_point[1]) if out_point else None,
            )
        )

    package_storages: typing.List[PackageStorage] = list()
    for ind, storages in enumerate(data['package_storages']):
        package_storages.append(
            PackageStorage(
                ind,
                Point.from_tuple(storages['locations']),
                storages['types'],
            )
        )

    storage_system = StorageSystem(
        map_storage,
        package_conveyors,
        package_storages,
        robots,
    )
    with open(args.log_file, 'w') as log_file:
        ant_ctrl_sys = AntControllerStorageSys(
            storage_system,
            data['max_package'],
            log_file,
        )
        ant_ctrl_sys.run()
    print(map_storage)
