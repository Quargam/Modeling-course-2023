import argparse
from pathlib import Path
import typing
import csv

import matplotlib.pyplot as plt


class CommandArgument(typing.Protocol):
    args: Path


def parse_arguments(arg_parser: argparse.ArgumentParser) -> None:
    arg_parser.add_argument(
        dest='args',
        metavar='PARAM.csv',
        type=Path,
    )
    arg_parser.set_defaults(command=exec_command)


def exec_command(args: CommandArgument) -> None:
    with open(args.args, 'r') as csv_file:
        csv_reader = csv.reader(csv_file)
        next(csv_reader)

        mail_and_robot_times: dict = {}
        mail_times: dict = {}
        for row in csv_reader:
            if not row:
                continue
            time, id_action, id_robot, _, _, desc = row
            if id_action == '1':
                type_mail = desc.split()[3]
                if mail_and_robot_times.get((type_mail, id_robot), None):
                    mail_and_robot_times[(type_mail, id_robot)].append(int(time) * -1)
                else:
                    mail_and_robot_times[(type_mail, id_robot)] = [int(time) * -1]
                    mail_times[type_mail] = []
            elif id_action == '0':
                type_mail = desc.split()[3]
                mail_and_robot_times[(type_mail, id_robot)][-1] = \
                    mail_and_robot_times[(type_mail, id_robot)][-1] + int(time)
            else:
                pass
        for mails_and_robots, times in mail_and_robot_times.items():
            mail_times[mails_and_robots[0]] += times

        _, axs = plt.subplots(len(mail_times), 1, figsize=(6, 8))
        for i, (mail, times) in enumerate(mail_times.items()):
            axs[i].hist(times, bins=range(0, 50), edgecolor='black')
            axs[i].set_title(f'Гистограмма для {mail}')
            axs[i].set_xlabel('время доставки')
            axs[i].set_ylabel('Количество посылок')

        plt.tight_layout()
        plt.show()
