import logging

logger = logging.getLogger(__name__)

__version__ = "2.7.2"


def get_version(thing=None):
    if thing is None:
        return __version__
    return "{thing} v{version}".format(thing=thing, version=__version__)
