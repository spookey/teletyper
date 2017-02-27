from argparse import ArgumentParser
from logging import getLogger

from teletyper.lib import APP_NAME
from teletyper.lib.disk import (
    base_location, ensured_folder, ensured_parent_folder
)
from teletyper.lib.logs import LOG_LEVEL
from teletyper.main import RUN_MODES

LOG = getLogger(__name__)


def check_args(args):
    args.config_file = ensured_parent_folder(args.config_file)
    args.log_folder = ensured_folder(args.log_folder)
    args.log_level = args.log_level.lower()
    args.mode = args.mode.lower()
    print(args)
    return args


def arguments():
    parser = ArgumentParser(APP_NAME)
    parser.add_argument(
        '-c', '--conf', dest='config_file', help='config file location',
        default=base_location('config.yaml')
    )
    parser.add_argument(
        '-l', '--log', dest='log_folder', help='folder location for log files',
        default=base_location('logs')
    )
    parser.add_argument(
        '-v', '--lvl', dest='log_level', help='log output level',
        default='info', choices=LOG_LEVEL.keys()
    )
    parser.add_argument(
        '-m', '--mode', dest='mode', help='mode to run',
        default='bot', choices=RUN_MODES.keys()
    )

    return check_args(parser.parse_args())
