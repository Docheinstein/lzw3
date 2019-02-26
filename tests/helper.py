import os
import shutil
from typing import List
from unittest import TestCase

from lzw3.commons.constants import LZWConstants
from lzw3.commons.log import Logger
from lzw3.commons.utils import read_binary_file
from lzw3.compressor import LZWCompressor
from lzw3.decompressor import LZWDecompressor


def remove_folder(path: str):
    if os.path.exists(path):
        shutil.rmtree(path)


def create_folder(path: str):
    if not os.path.exists(path):
        os.makedirs(path)


class LZWTestHelper(TestCase):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.verbose = False
        Logger.enable_logger(False)

    def _test_files(self, files: List[str]):
        for file in files:
            uncompressed_file_path = file
            compressed_file_path = file + LZWConstants.COMPRESSED_FILE_EXTENSION
            decompressed_file_path = compressed_file_path + ".after"

            file_content = read_binary_file(uncompressed_file_path)

            self.__print("Compressing '" + uncompressed_file_path + "'")
            LZWCompressor().compress(
                uncompressed_file_path,
                compressed_file_path
            )

            self.__print("Decompressing '" + compressed_file_path + "'")
            LZWDecompressor().decompress(
                compressed_file_path,
                decompressed_file_path
            )

            file_content_after = read_binary_file(decompressed_file_path)
            self.assertEqual(file_content, file_content_after,
                             "Content after compression and decompression of file '"
                             + file + "' is not the same!")
            self.__print("")

    def __print(self, *args, **kwargs):
        if self.verbose:
            print(*args, **kwargs)
