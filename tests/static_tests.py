import os
import shutil
import unittest

from tests.helper import create_folder, remove_folder, LZWTestHelper

STATIC_FILES_OUTPUT_FOLDER = "/tmp/lzw/statics"
RESOURCES_FOLDER = "res"
RESOURCES = [
    "dhclient.conf",
    "hdparm.conf",
    "mcm_sellers.txt"
]


class LZWStaticTests(LZWTestHelper):

    def test_static(self):
        self.__test()

    def __test(self):
        remove_folder(STATIC_FILES_OUTPUT_FOLDER)
        create_folder(STATIC_FILES_OUTPUT_FOLDER)

        files = []

        self.__print("\n--- STATIC TESTS ---")

        for res_name in RESOURCES:
            current_path = os.path.abspath(os.path.dirname(__file__))
            res_path = os.path.join(current_path, RESOURCES_FOLDER, res_name)

            uncompressed_file_path = os.path.join(
                STATIC_FILES_OUTPUT_FOLDER,
                res_name
            )

            shutil.copy(res_path, uncompressed_file_path)

            files.append(uncompressed_file_path)

        self._test_files(files)

        self.__print("OK! Compressor and decompressor for static files (should) work")
        self.__print("--- END STATIC TESTS ---")

    def __print(self, *args, **kwargs):
        if self.verbose:
            print(*args, **kwargs)


if __name__ == '__main__':
    unittest.main()
