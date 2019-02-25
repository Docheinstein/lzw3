import os
import random
import unittest
from typing import Callable

from lzw3.commons.utils import humanify_bytesize
from tests.helper import LZWTestHelper, remove_folder, create_folder

RANDOM_FILES_OUTPUT_FOLDER = "/tmp/lzw/randoms"
INITIAL_FILE_SIZE = 1024
FILE_COUNT = 8
MAX_CHUNKS = 10


def create_random_file(path: str, size: int):
    with open(path, 'wb') as fout:
        fout.write(os.urandom(size))


def create_repeated_random_sequences_file(path: str, size: int):
    with open(path, 'wb') as fout:
        chunks = random.randint(1, MAX_CHUNKS)
        chunk_size = size // chunks
        bs = os.urandom(chunk_size)
        fout.write(bs * chunks)


class LZWRandomTests(LZWTestHelper):

    def test_truly_random(self):
        self.__test(create_random_file)

    def test_repeated_random_sequences(self):
        self.__test(create_repeated_random_sequences_file)

    def __test(self, create_file_function: Callable):
        sz = INITIAL_FILE_SIZE

        remove_folder(RANDOM_FILES_OUTPUT_FOLDER)
        create_folder(RANDOM_FILES_OUTPUT_FOLDER)

        files = []

        self.__print("\n--- RANDOM TESTS ---")

        for i in range(FILE_COUNT):
            file_name = "r" + str(i) + ".bin"

            uncompressed_file_path = os.path.join(
                RANDOM_FILES_OUTPUT_FOLDER,
                file_name
            )

            self.__print("Creating random file '" + uncompressed_file_path +
                         "' of size = " + humanify_bytesize(sz))
            create_file_function(uncompressed_file_path, sz)
            sz *= 2

            files.append(uncompressed_file_path)

        self._test_files(files)

        self.__print("OK! Compressor and decompressor for random files (should) work")
        self.__print("--- END RANDOM TESTS ---")

    def __print(self, *args, **kwargs):
        if self.verbose:
            print(*args, **kwargs)


if __name__ == '__main__':
    unittest.main()
