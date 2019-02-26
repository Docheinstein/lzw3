import os
import sys
from typing import List

from lzw3.helpers import LZWHelper, LZWHelperStarter
from lzw3.io.byte import ByteWriter
from lzw3.io.bit import BitReader

from lzw3.commons.log import Loggable, Logger
from lzw3.commons.constants import LZWConstants, Resources
from lzw3.commons.utils import timed, file_permission_mask, humanify_ms


class LZWDecompressor(Loggable):
    """ Decompressor of regular files that use LZW algorithm. """

    def _get_logger_tag(self) -> str:
        return "DECOMPRESSOR"

    def _can_log(self) -> bool:
        return False

    def __init__(self):
        super().__init__()
        self._in_file = None
        self._out_file = None

    def decompress(self, in_file_path: str, out_file_path: str) -> bool:
        """ Decompresses the given input file to the output file

        Args:
            in_file_path (str): the path of the compressed file
            out_file_path (str): the path of the file that will contain
                the uncompressed content of the input file

        Returns:
            bool: whether the file (exists and) has been decompressed successfully
        """
        if not os.path.exists(in_file_path):
            self._log("Decompression failed! File '" + in_file_path + "' doesn't exists")
            return False

        self._init()

        self._log("Decompressing file '", in_file_path, "' to '", out_file_path, "'")

        self._in_file = BitReader(in_file_path)
        self._out_file = ByteWriter(out_file_path)

        # Before start the main loop we have to read the first sequence
        # (which must be an alphabet sequence) and place it to output
        seq_parent = self._in_file.read(self._current_sequence_bit_count)
        seq_parent_path = self._get_sequence_path(seq_parent)

        # self._log(">> ", seq_parent_path)
        self._out_file.write(seq_parent_path)

        seq_path = seq_parent_path
        seq_path_first = seq_parent_path[0]

        for seq in self._in_file:
            # self._log("<< {", seq, "}")

            # STREAM_END reached (EOF)
            if seq == LZWConstants.STREAM_END:
                break

            is_normal_case = seq < self._next_sequence_number

            # "Normal" case, the read sequence number is well known so
            # the seq_path is assigned to the path to reach the sequence number
            if is_normal_case:
                seq_path = self._get_sequence_path(seq)
                seq_path_first = seq_path[0]

            # For both the "normal" and the "special" case the sequence path to
            # insert is the previous sequence path plus the first component
            # of the current sequence path (which is the same path for the
            # "special" case)
            new_seq_path = seq_parent_path + [seq_path_first]

            # Add the new sequence path using the next sequence number
            # self._log("+= ", new_seq_path, " = ", self._next_sequence_number)
            self._insert_next_sequence_path(new_seq_path)

            if is_normal_case:
                # For the "normal" case the path to write is the one
                # associated with the read sequence number
                seq_out_path = seq_path
            else:
                # For the "special" case the path to write is the just created
                # one since we do not have that path in our table yet
                seq_out_path = new_seq_path

            # Write the path to the output file
            # self._log(">> ", seq_out_path)
            self._out_file.write(seq_out_path)

            # Continue from the path we've just wrote to file
            seq_parent_path = seq_out_path

            # Set the amount of bits to read for the next read
            self._in_file.set_bits_per_read(self._current_sequence_bit_count)

            # self._log("---")

        self._in_file.close()
        self._out_file.close()

        return True

    def _init(self):
        """ Initializes the decompressor with the initial setup. """

        # List for keep the sequences;
        # Each element is a list of integers € [0, 255] that represents the path
        # from the ROOT node (excluded) to the sequence number associated with the
        # position of the element in the list.
        # e.g. A sequence 'ABC' with sequence number 275 will be placed in
        # _sequence_table[275] = [65 (A), 66 (B), 67 (C)]
        self._sequence_table = []

        # Number that will be associated to the next sequence
        self._next_sequence_number = 0

        # Number of bits necessary for represents the current sequence number
        self._current_sequence_bit_count = 0

        self._log("Initializing sequence table; alphabet size = ",
                  LZWConstants.ALPHABET_SIZE)

        # Alphabet characters initialization
        for i in range(LZWConstants.ALPHABET_SIZE):
            self._insert_next_sequence_path([i])

        # Special character for STREAM_END
        self._insert_next_sequence_path([LZWConstants.STREAM_END])

    def _insert_next_sequence_path(self, seq_path: List[int]):
        """ Inserts the given path to the table using the next sequence number.

        Args:
            seq_path (:obj:`list` of :obj:`int`): the path as list of integer,
                where each element represent the ASCII code of a character
                that composes the sequence.
        """
        # Actually there is not need to call .insert(self._next_sequence_number, seq_path)
        # since the sequence numbers begin from 0 and so the append() and the
        # insert() would do the same thing.
        self._sequence_table.append(seq_path)

        self._next_sequence_number += 1

        # Increment the number of bits required for represent the sequence
        # if the next sequence number has a new bit set to 1.
        # (This is a reasonable way to avoid to call log2 each time, and works
        # because the sequence number are progressive).
        # The decompressor switches to the new bit size one step before the compressor
        self._current_sequence_bit_count += \
            (self._next_sequence_number >> self._current_sequence_bit_count)

    def _get_sequence_path(self, seq: int) -> List[int]:
        """ Returns the path associated with the given sequence number.

        Args:
            seq (int): the sequence number of the path to retrieve

        Returns:
            (:obj:`list` of :obj:`int`): the path as list of integer,
                where each element represent the ASCII code of a character
                that composes the sequence.
        """
        return self._sequence_table[seq]


class LZWDecompressorHelper(LZWHelper):
    """
    An helper that invoke LZWDecompressor.decompress() and handles some more logic.
    """

    def _get_logger_tag(self) -> str:
        return "DECOMPRESSOR_HELPER"

    def _can_log(self) -> bool:
        return True

    def _handle_file(self, file: str):
        """ Handles the (regular) file by decompressing it.
        Some more logic is handled:
        <ul>
        </ul>
        1) Whether skip the decompression if the input file doesn't end with
           the .Z extension
        2) Where to place the decompressed file
        3) Copy the permission mask to the decompressed file
        4) Print messages and decompression times, if enabled

        Args:
            file (str): the path of the file to handle
        """

        # Skips decompression for non .Z files; this is convenient in order
        # to use the compressor in a recursive manner and then the decompressor
        # on the same folder, since the compressor could leave some file
        # uncompressed
        # Decompress anyhow if the force flag (-f) is specified

        if file.endswith(LZWConstants.COMPRESSED_FILE_EXTENSION):
            # The name of the uncompressed file is the same without the .Z at the end
            file_out = file[:(len(file) - len(LZWConstants.COMPRESSED_FILE_EXTENSION))]
            in_place = False
        elif self._force:
            self._log("File '", file, "' doesn't end with ",
                      LZWConstants.COMPRESSED_FILE_EXTENSION,
                      "; handling it anyhow due force flag (-f)")
            file_out = file
            in_place = True
        else:
            self._log("File '", file, "' doesn't end with ",
                      LZWConstants.COMPRESSED_FILE_EXTENSION,
                      "; skipping it")
            self._print("'", file, "' skipped")
            return

        time_string = " "

        in_decompression_file_string = "'" + file + "'"

        if not Logger.is_logger_enabled():
            # Print the name of the file now so that the user may now what's
            # going on for slow decompressions, if logger is enabled this can't
            # be done since the further debug messages will break the prints
            self._print("'", file, "'", end="", flush=True)
            in_decompression_file_string = ""

        # Measure the compression time if required
        if self._time:
            ms = timed(LZWDecompressor.decompress, LZWDecompressor(), file, file_out)
            time_string = " (" + humanify_ms(ms) + ")"
        else:
            LZWDecompressor().decompress(file, file_out)

        self._log("Decompression finished", time_string)
        self._print(in_decompression_file_string, " decompressed", time_string)

        if not in_place:
            # Retrieve perm mask of the file
            perm_mask = file_permission_mask(file)

            if not self._keep:
                self._log("--> (Deleting compressed file)")
                os.remove(file)
            else:
                self._log("--> (Keeping compressed file)")

            # Write permissions on the new file copying to the old ones
            self._log("Writing previous permissions to new file = ", file_permission_mask)
            os.chmod(file_out, perm_mask)


def main():
    LZWHelperStarter(LZWDecompressorHelper, Resources.UNCOMPRESS_HELP) \
        .start(sys.argv[1:])


if __name__ == '__main__':
    main()
