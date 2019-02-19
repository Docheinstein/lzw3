class LZWConstants:
    ROOT = -1
    """ Integer value for represents the root of the sequences. """

    ALPHABET_SIZE = 256
    """ Size of the alphabet. """

    STREAM_END = ALPHABET_SIZE
    """ Value of the sequence that represents the EOF. """

    COMPRESSED_FILE_EXTENSION = ".Z"
    """ Extension that will be appended or checked for LZW compressed files. """


class Resources:
    COMPRESS_HELP = "compress_help.txt"
    UNCOMPRESS_HELP = "uncompress_help.txt"


class SizeUnits:
    K = 1024
    M = K * K


class TimeUnits:
    SEC_IN_MIN = 60
    MS_IN_SEC = 1000
    MS_IN_MIN = MS_IN_SEC * SEC_IN_MIN
