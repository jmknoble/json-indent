# fmt: off

__author__ = 'Jim Knoble'
__email__ = 'jmknoble@pobox.com'
__version__ = '2.6.3'

# fmt: on


def get_version(thing=None):
    if thing is None:
        return __version__
    return "{thing} v{version}".format(thing=thing, version=__version__)
