from collections import namedtuple
from json import dumps
from logging import getLogger
from os import makedirs, path, remove, walk
from shutil import rmtree

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


def destroy_location(*location):
    location = join_location(*location)
    LOG.warning('deleting location "%s"', location)
    if check_location(location, folder=True):
        return rmtree(location)
    return remove(location)


def read_file(*location, fallback=None):
    location = join_location(*location)
    if not check_location(location, folder=False):
        LOG.warning(
            'no such file "%s" return fallback "%s"', location, fallback
        )
        return fallback
    with open(location, 'r') as handle:
        LOG.info('reading file "%s"', location)
        content = handle.read()
        if content is not None:
            return content
    LOG.warning('file empty "%s" return fallback "%s"', location, fallback)
    return fallback


def read_yaml(*location, fallback=None):
    location = join_location(*location)
    if not check_location(location, folder=False):
        LOG.warning(
            'no such yaml "%s" return fallback "%s"', location, fallback
        )
        return fallback
    with open(location, 'r') as handle:
        LOG.info('reading yaml "%s"', location)
        content = load(handle)
        if content is not None:
            return content

    LOG.warning('yaml empty "%s" return fallback "%s"', location, fallback)
    return fallback


def write_file(*location, content):
    location = ensured_parent_folder(*location)
    with open(location, 'w') as handle:
        LOG.info('writing file "%s"', location)
        return handle.write(content)


def write_json(*location, content):
    return write_file(*location, content=dumps(
        content, indent=2, sort_keys=True
    ))


def write_yaml(*location, content):
    location = ensured_parent_folder(*location)
    with open(location, 'w') as handle:
        LOG.info('writing yaml "%s"', location)
        return dump(
            content, stream=handle,
            allow_unicode=True, canonical=False, default_flow_style=False,
            explicit_end=False, explicit_start=False, indent=4
        )


def walk_location(*location):
    location = join_location(*location)
    element = namedtuple('path', ('full', 'base', 'inner', 'name', 'is_file'))

    def result(directory, name, is_file):
        full = join_location(directory, name)
        return element(
            base=location,
            full=full,
            inner=full.partition(location)[-1].lstrip('/'),
            is_file=is_file,
            name=name,
        )

    if check_location(location, folder=True):
        LOG.info('walking tree "%s"', location)
        for directory, folders, files in walk(location):
            for file_name in files:
                yield result(directory, file_name, True)
            for folder_name in folders:
                yield result(directory, folder_name, False)
