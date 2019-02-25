import pkg_resources

from lzw3.commons.utils import read_textual_file


def read_textual_resource(res: str) -> str:
    """ Reads the content of the given resource.
    The resource is loaded relatively to the path "res/"
    using pkg_resources of setuptools.

    Args:
        res (str): the path of the resource relative to "res/"

    Returns:
        str: the content of the resource file
    """
    return read_textual_file(pkg_resources.resource_filename(__name__, res))

