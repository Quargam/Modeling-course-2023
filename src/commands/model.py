import argparse
from pathlib import Path
import typing
import yaml


class CommandArgument(typing.Protocol):
    args: Path


def parse_arguments(arg_parser: argparse.ArgumentParser) -> None:
    arg_parser.add_argument(
        dest='args',
        metavar='PARAM.yaml',
        type=Path,
    )
    arg_parser.set_defaults(command=exec_command)


def exec_command(args: CommandArgument) -> None:
    with open(args.args, 'r') as stream:
        data = yaml.safe_load(stream)
        print(data)
