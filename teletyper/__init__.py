from teletyper.conf import Conf
from teletyper.lib import APP_NAME
from teletyper.lib.args import arguments
from teletyper.lib.logs import logger
from teletyper.main import RUN_MODES


def run():
    args = arguments()
    log = logger(__name__, args.log_folder, args.log_level)
    log.debug('==> %s <%s', APP_NAME, '=' * (32 - 6 - len(APP_NAME)))
    conf = Conf(args.config_file)
    mod = RUN_MODES.get(args.mode)
    if mod is not None:
        log.info('run mode: %s', args.mode)
        return mod(conf)
    return False
