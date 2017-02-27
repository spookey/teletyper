from logging import getLogger
from os import makedirs, path

from yaml import dump, load

LOG = getLogger(__name__)


def join_location(*location, absolute=True):
    location = path.join(*location)
    if absolute:
        location = path.abspath(location)
    return location


def base_location(*location):
    base = path.dirname(path.dirname(path.dirname(path.abspath(__file__))))
    if location:
        return join_location(base, *location)
    return base


def check_location(*location, folder=False):
    location = join_location(*location)
    function = path.isdir if folder else path.isfile
    return path.exists(location) and function(location)


def ensured_folder(*location):
    location = join_location(*location)
    if not check_location(location, folder=True):
        LOG.info('creating folder "%s"', location)
        makedirs(location)
    return location


def ensured_parent_folder(*location):
    location = join_location(*location)
    ensured_folder(path.dirname(location))
    return location


def read_yaml(*location, fallback=None):
    location = join_location(*location)
    if not check_location(location, folder=False):
        LOG.info('no such yaml "%s" return fallback "%s"', location, fallback)
        return fallback
    with open(location, 'r') as handle:
        LOG.debug('reading yaml "%s"', location)
        content = load(handle)
        if content is not None:
            return content

    LOG.warning('yaml empty "%s" return fallback "%s"', location, fallback)
    return fallback


def write_yaml(*location, content):
    location = ensured_parent_folder(*location)
    with open(location, 'w') as handle:
        LOG.debug('writing yaml "%s"', location)
        return dump(
            content, stream=handle,
            allow_unicode=True, canonical=False, default_flow_style=False,
            explicit_end=False, explicit_start=False, indent=4
        )
