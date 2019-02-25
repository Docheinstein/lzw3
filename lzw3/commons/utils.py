import math
import os
import time
from collections import Callable
from typing import Union

from lzw3.commons.constants import SizeUnits, TimeUnits


def read_textual_file(path: str) -> str:
    """ Reads the content of the given textual file.
    Args:
        path (str): the path of the file

    Returns:
        str: the content of the textual file
    """
    return read_file(path, "r")


def read_binary_file(path: str) -> bytes:
    """ Reads the content of the given binary file.
    Args:
        path (str): the path of the file

    Returns:
        bytes: the content of the binary file
    """
    return read_file(path, "rb")


def read_file(path: str, mode: str) -> Union[str, bytes]:
    """ Reads the content of the given file.
    Args:
        path (str): the path of the file
        mode (str): the open mode, could be "r" or "rb"

    Returns:
        the content of the file, as string or bytes depending on the mode
    """
    with open(path, mode) as f:
        return f.read()


def timed(fun: Callable, *args, **kwargs) -> int:
    """ Returns the execution time of a function in milliseconds.
    The return value of the function is discarded since the exec time will
    be returned by this invocation.

    Args:
        fun (Callable): the function to call
        *args: the arguments to pass to the function
        **kwargs: the keyword arguments to pass to the function

    Returns:
        int: the amount of milliseconds for execute the function
    """
    t_start = time.time()
    fun(*args, **kwargs)
    t_end = time.time()

    return round((t_end - t_start) * 1000)


def file_permission_mask(file: str) -> int:
    """ Returns the file permissions mask of the file.

    Args:
        file (str): the path of the file

    Returns:
        int: an integer that represent the permission mask of the file.
            i.e. the maximum value of the mask is 0o7777
    """
    return permission_mask(os.stat(file))


def permission_mask(st_result: os.stat_result) -> int:
    """ Returns the file permissions mask of the stat result of a file.
    Can be useful instead of get_file_permission_mask() if a stat_result
    has been retrieved for other purposes in order to avoid other calls to stat()

    Args:
        st_result (os.stat_result): the result of os.stat(file)

    Returns:
        int: an integer that represent the permission mask of the file.
            i.e. the maximum value of the mask is 0o7777
    """
    return st_result.st_mode & 0o7777


def humanify_bytesize(bytesize: int) -> str:
    """ Converts a byte size to a more readable string.
    e.g. 750 => 750B, 4096 => 4K

    Args:
        bytesize (int): the size to convert to string

    Returns:
        The human string that represents the given bytesize.
    """
    if bytesize >= SizeUnits.M:
        return "{:.1f}M".format(bytesize / SizeUnits.M)
    if bytesize >= SizeUnits.K:
        return "{:.1f}K".format(bytesize / SizeUnits.K)
    return "{:d}B".format(bytesize)


def humanify_ms(ms: int) -> str:
    """ Converts an amount of millis to a more readable string.

    Args:
        ms (int): the amount of millis to convert

    Returns:
        The human string that represents the given amount of millis
    """
    if ms > TimeUnits.MS_IN_MIN:
        return "{:d}m {:d}s".format(
            math.floor(
                ms / TimeUnits.MS_IN_MIN
            ),
            math.floor(
                (ms % TimeUnits.MS_IN_MIN) / TimeUnits.MS_IN_SEC
            )
        )
    if ms > TimeUnits.MS_IN_SEC:
        return "{:.2f}s".format(ms / 1000)
    return "{:d}ms".format(ms)
