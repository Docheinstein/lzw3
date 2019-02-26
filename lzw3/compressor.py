import os
import sys
from typing import Union

from lzw3.helpers import LZWHelper, LZWHelperStarter
from lzw3.io.bit import BitWriter
from lzw3.io.byte import ByteReader

from lzw3.commons.log import Loggable, Logger
from lzw3.commons.constants import LZWConstants, Resources
from lzw3.commons.utils import timed, permission_mask, humanify_bytesize, humanify_ms


class LZWCompressor(Loggable):
    """ Compressor of regular files that use LZW algorithm. """
    
    def _get_logger_tag(self) -> str:
        return "COMPRESSOR"

    def _can_log(self) -> bool:
        return True

    def __init__(self):
        super().__init__()
        self._in_file = None
        self._out_file = None

    def compress(self, in_file_path: str, out_file_path: str) -> bool:
        """ Compresses the given input file to the output file.

        Args:
            in_file_path (str): the path of the (regular) file to compress
            out_file_path (str): the path of the file that will contain
                the compressed content of the input file

        Returns:
            bool: whether the file (exists and) has been compressed successfully
        """
        if not os.path.exists(in_file_path):
            self._log("Compression failed! File '" + in_file_path + "' doesn't exists")
            return False

        self._init()

        self._log("Compressing file '", in_file_path, "' to '", out_file_path, "'")

        self._in_file = ByteReader(in_file_path)
        self._out_file = BitWriter(out_file_path)

        # Start from the ROOT (empty sequence)
        seq_parent = LZWConstants.ROOT

        for c in self._in_file:
            # self._log("<< {", c, "} (", chr(c), ")")

            # Retrieve the sequence associated with the character just read
            # appended to the sequence read so far
            seq = self._get_sequence(seq_parent, c)
            # self._log("| ", seq_parent, " --{", c, "}-->  ", seq)

            if seq is not None:
                # We have read a character for a known sequence.
                #
                # Go ahead until a None sequence is found and
                # continue from this sequence leaf.
                seq_parent = seq
            else:
                # We have read a character that makes the sequence unknown.

                # Write to file the sequence read so far (without this character)
                # self._log(">> ", seq_parent)
                self._write_sequence(seq_parent)

                # Add the new sequence using the next sequence number
                # self._log("+= ", seq_parent, " --{", c, "}--> ", self._next_sequence_number)
                self._insert_next_sequence(seq_parent, c)

                # Restart from the sequence of this character
                seq_parent = self._get_sequence(LZWConstants.ROOT, c)

            # self._log("---")

        # Write the last character; this is necessary in both case
        # 1) If the read sequence was recognized with the last char
        #    nothing is printed since a new char is expected but the loop ends
        #    so the sequence has to be written
        # 2) If the read sequence was not recognized due the last char
        #    then the sequence minus the last char has been written,
        #    so there is still need to write the last char
        # self._log(">> ", seq_parent)
        self._write_sequence(seq_parent)

        # self._log("Input file stream's ended")

        # Write the STREAM_END character so that the decompressor can detect it.
        # self._log(">> ", LZWConstants.STREAM_END)
        self._write_sequence(LZWConstants.STREAM_END)

        self._in_file.close()
        self._out_file.close()

        return True

    def _init(self):
        """ Initializes the compressor with the initial setup. """

        # Dictionary for keep the sequences; the structure is the following
        # ( K, V ) = ( (ParentSeqNum: int, EdgeToChild: int(0:255), ChildSeqNum: int )
        self._sequence_table = dict()

        # Number that will be associated to the next sequence
        self._next_sequence_number = 0

        # Number of bits necessary for represents the current sequence number
        self._current_sequence_bit_count = 0

        self._log("Initializing sequence table; alphabet size = ",
                  LZWConstants.ALPHABET_SIZE)

        # Alphabet characters initialization
        for i in range(LZWConstants.ALPHABET_SIZE):
            self._insert_next_sequence(LZWConstants.ROOT, i)

        # Special character for STREAM_END
        self._insert_next_sequence(LZWConstants.ROOT, LZWConstants.STREAM_END)

    def _insert_next_sequence(self, parent_seq: int, edge: int):
        """ Inserts the next sequence number for the given parent and edge.

        Args:
            parent_seq (int): the sequence value of the leaf of the parent
                of the sequence that will be inserted
            edge (int): the label of the edge that links the given parent to
                the sequence that will be inserted; should be < ALPHABET_SIZE
        """
        self._sequence_table[(parent_seq, edge)] = self._next_sequence_number

        # Increment the number of bits required for represent the sequence
        # if this sequence number has a new bit set to 1.
        # (This is a reasonable way to avoid to call log2 each time, and works
        # because the sequence number are progressive)
        self._current_sequence_bit_count += \
            (self._next_sequence_number >> self._current_sequence_bit_count)

        self._next_sequence_number += 1

    def _get_sequence(self, parent_seq: int, edge: int) -> Union[int, None]:
        """
        Returns the sequence associated with the leaf found starting from
        the given parent and descending using the given edge.

        Args:
            parent_seq (int): the sequence value of the leaf of the parent
                of the sequence to find
            edge (int): the label of the edge that links the given parent to
                the sequence to find; should be < ALPHABET_SIZE

        Returns:
            int: the sequence found descending from parent_seq using edge or
                None if it doesn't exist
        """
        return self._sequence_table.get((parent_seq, edge), None)

    def _write_sequence(self, seq: int):
        """ Writes the given sequence to the output file.

        Args:
            seq (int): the sequence number to write to the output file.
                This will automatically be written with the right amount
                of bits to represents it.
        """
        self._out_file.write(seq, self._current_sequence_bit_count)


class LZWCompressorHelper(LZWHelper):
    """
    An helper that invoke LZWCompressor.compress() and handles some more logic.
    """

    def _get_logger_tag(self) -> str:
        return "COMPRESSOR_HELPER"

    def _can_log(self) -> bool:
        return False

    def _handle_file(self, file: str):
        """ Handles the (regular) file by compressing it.
        Some more logic is handled:
        <ul>
        </ul>
        1) Where to place the compressed file
        2) Whether keep the original file if the size of the compressed one
           is higher then the original
        3) Copy the permission mask to the compressed file
        4) Print messages and compression times, if enabled

        Args:
            file (str): the path of the file to handle
        """
        # Retrieve size and perm mask of the file
        file_stat = os.stat(file)
        uncompressed_size = file_stat.st_size
        perm_mask = permission_mask(file_stat)

        self._log("Going to compress file '", file, "' of size = ", uncompressed_size, "B")

        # The output path is the input path plus .Z
        file_out = file + LZWConstants.COMPRESSED_FILE_EXTENSION

        time_string = " "

        in_compression_file_string = "'" + file + "'"

        if not Logger.is_logger_enabled():
            # Print the name of the file now so that the user may now what's
            # going on for slow compressions, if logger is enabled this can't
            # be done since the further debug messages will break the prints
            self._print("'", file, "'", end="", flush=True)
            in_compression_file_string = ""

        # Measure the decompression time if required
        if self._time:
            ms = timed(LZWCompressor.compress, LZWCompressor(), file, file_out)
            time_string = " (" + humanify_ms(ms) + ")"
        else:
            LZWCompressor().compress(file, file_out)

        compressed_size = os.path.getsize(file_out)
        self._log("Compression finished", time_string,
                  " compressed file size would be = ", compressed_size, "B")

        # Check whether keep the compressed file instead of the uncompressed one
        if self._force or compressed_size < uncompressed_size:

            if compressed_size < uncompressed_size:
                self._log("--> OK! Compressed file size is lower than the original size")
            else:
                self._log("Keeping the file even if the size is higher "
                          "than the original size due force flag (-f)")

            # Calculate the percentage of space saved with the compression
            compression_saving = (1 - (compressed_size / uncompressed_size)) * 100

            self._print(in_compression_file_string, " compressed from ",
                        humanify_bytesize(uncompressed_size), " to ",
                        humanify_bytesize(compressed_size),
                        " - space saved = {:02.1f}%".format(compression_saving),
                        time_string)

            if not self._keep:
                self._log("--> (Deleting uncompressed file)")
                os.remove(file)
            else:
                self._log("--> (Keeping uncompressed file)")

            # Write permissions to the new file copying to the old ones
            self._log("Writing previous permissions to new file = ", perm_mask)
            os.chmod(file_out, perm_mask)
        else:
            self._log("--> OPS! Compressed file size is not lower than the original size, "
                      "removing it and keeping the old one")
            self._print(in_compression_file_string, " left uncompressed", time_string)
            os.remove(file_out)


def main():
    LZWHelperStarter(LZWCompressorHelper, Resources.COMPRESS_HELP) \
        .start(sys.argv[1:])


if __name__ == '__main__':
    main()
