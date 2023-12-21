import argparse
import typing
import sys


from src.commands import model


def parse_arguments(cmd_args: typing.Optional[typing.List[str]]) -> argparse.Namespace:
    arg_parser = argparse.ArgumentParser()
    subparsers = arg_parser.add_subparsers()
    model.parse_arguments(subparsers.add_parser(
        'model',
    ))
    return arg_parser.parse_args(cmd_args)


def main(cmd_args: typing.Optional[typing.List[str]]) -> None:
    args = parse_arguments(cmd_args)
    args.command(args)  # Запуск команды с аргументом.


if __name__ == '__main__':
    main(sys.argv[1:])
