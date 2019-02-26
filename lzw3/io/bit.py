from lzw3.commons.log import Loggable

BYTE_SIZE = 8
BYTE_MASK = 0xFF  # 1111 1111


class BitReader(Loggable):
    """ Entity that provides a way to read a chunk of bit from a file.
    The reading can easily be done by iterate over this entity.

    The chunk size must be specified so that this reader actually reads
    the right amount of bits.
    """

    def _get_logger_tag(self) -> str:
        return "BIT_READER"

    def _can_log(self) -> bool:
        return False

    def __init__(self,
                 in_file_path: str,
                 bits_per_read: int = BYTE_SIZE,
                 buffer_size: int = None):
        """ Initializes a new BitReader for the given file, actually opening it.

        Args:
            in_file_path (str): the path of the file that will be read
            bits_per_read (int): initial amount of bits to read for each read,
                can be eventually changed after, even during the iteration
                over this entity
            buffer_size (int): the size of the buffer to use for reads,
                if not provided the default size will be used.
        """
        super().__init__()

        if buffer_size is not None:
            self._file = open(in_file_path, "rb", buffering=buffer_size)
        else:
            self._file = open(in_file_path, "rb")

        # Amount of bit the consumer expects we read from the file
        self._bits_per_read = bits_per_read

        # Amount of unaligned bits we have read from the file so far
        # Is always < 8 since we never reads more byte then the minimum amount
        # we need to create the value
        self._read_bit_count = 0

        # Value of the unaligned amount of bits (read_bit_count) we have read
        # so far.
        # Since read_bit_count is always < 8, this is always <= 128
        self._unaligned_rest = 0

        # Whether we have reached EOF and so we have to raise StopIteration
        # for the next call
        self._eof = False

    def __iter__(self):
        """ Returns an iterator for read the file as chunks of bits
        Returns:
            this entity as an iterator for read the file as chunks of bits
        """
        return self

    def __next__(self) -> int:
        """ Reads the next chunk of bits from the file.
        The amount of bits read from the file is 'bits_per_read', settable
        via set_bits_per_read().

        Returns:
            int: the integer value of the chunk of bits read from the file.
                e.g. read_per_bits = 8,  read:    0001 0000 => 16
                     read_per_bits = 10, read: 01 0001 0001 => 273
        """
        if self._eof:
            raise StopIteration

        # Sum the value remained from the unaligned bits of the last read
        v = self._unaligned_rest

        # Read bytes until we reached a count of read bytes greater
        # than the number of bits (* 8) we have to read
        while self._read_bit_count < self._bits_per_read:
            B = self._file.read(1)
            if B:
                # Sum the value of the just read byte with the previous
                # value, shifted by 8 so that the result is just a concatenation
                # of the previous bits and this byte
                v = B[0] | (v << BYTE_SIZE)

                # We have read 8 more bit, advance the count
                self._read_bit_count += BYTE_SIZE

                # self.log("Read byte {", c[0], "}, v = ", v)
            else:
                # When EOF is reached we should not raise StopIteration
                # since we might still have a certain unaligned amount
                # of bits to yield; instead return the unaligned_rest
                # and raise StopIteration with the next iteration

                # self.log("EOF reached, returning remaining value")
                self._eof = True
                return self._unaligned_rest

        # Set the amount of bits read equals to the unaligned amount of bits
        # remained out from the creation of this value.
        # e.g. If we have read 2 byte (16 bits) but we have been request to
        # provide a value for a length of 14 bits, then we have read 2 bit more
        # that we have to keep into consideration for the next read, so
        # read_bit_count will be = 2
        self._read_bit_count -= self._bits_per_read

        # The rest is calculated by considering only the bits taken out from
        # this value, which actually is done by consider only the first
        # (8 - read_bit_count) bits of the value
        # e.g. If we have read 16 bits we provided a value for 14, then
        # the unaligned_rest is the first 2 least significant bits of the value
        self._unaligned_rest = v & (BYTE_MASK >> (BYTE_SIZE - self._read_bit_count))

        # And finally the value is calculated as the value shifted by the
        # amount of bits that we have read in excess
        v = v >> self._read_bit_count

        # self.log("read_bit_count: ", self._read_bit_count)
        # self.log("unaligned_rest: ", self._unaligned_rest)

        return v

    def read(self, bits_per_read: int = None) -> int:
        """ Reads the next chunk of bits from the file.
        The amount of bits read from the file is 'bits_per_read', settable
        via set_bits_per_read().
        Can be preferred over __next__() for take only a single chunk.

        Args:
            bits_per_read (int): amount of bits to read for this and the
                successive reads. If not specified the current bits_per_read
                amount will be read

        Returns:
            int: the integer value of the chunk of bits read from the file.
                e.g. read_per_bits = 8,  read:    0001 0000 => 16
                     read_per_bits = 10, read: 01 0001 0001 => 273
        """
        if bits_per_read is not None:
            self._bits_per_read = bits_per_read
        return self.__next__()

    def set_bits_per_read(self, bits_per_read: int):
        """ Sets the amount of bits to read from the file.
        Actually it should be more appropriate to say: sets the amount of bits
        to take into consideration for make the next integer that will be
        given by read() or __next__(), since the file is actually read byte
        per byte anyway.

        Args:
            bits_per_read (int): amount of bits to read for each read

        """
        self._bits_per_read = bits_per_read

    def close(self):
        """ Closes the file. """
        self._file.close()


class BitWriter(Loggable):
    """ Entity that provides a way to write raw bits to a file. """

    def _get_logger_tag(self) -> str:
        return "BIT_WRITER"

    def _can_log(self) -> bool:
        return True

    def __init__(self, out_file_path: str, buffer_size : int = None):
        """ Initializes a new BitWriter for the given file, actually opening it.

        Args:
            out_file_path (str): the path of the file that will be written
            buffer_size (int): the size of the buffer to use for writes,
                if not provided the default size will be used.
        """
        super().__init__()

        if buffer_size is not None:
            self._file = open(out_file_path, "wb", buffering=buffer_size)
        else:
            self._file = open(out_file_path, "wb")

            # Amount of unaligned bits we have read from the file so far
            # Is always < 8 since we never reads more byte then the minimum amount
            # we need to create the value

        # Amount of unaligned bits we still have to write to the file, but we
        # can do since we still don't have a full byte to write.
        # Is always < 8 (since if it reaches 8 the byte is actually written)
        self._unalignment = 0

        # Value of the unaligned amount of bits (read_bit_count)
        # we still have to write to the file.
        # Since read_bit_count is always < 8, this is always < 128
        self._unaligned_rest = 0

        # This is kept as class variable in order to avoid to reallocate
        # a bytes() each time. (Whereas bytearray is mutable).
        # Only _B[0] will be used, as a single byte.
        self._B = bytearray(1)

    def write(self, value: int, bits_per_write: int):
        """
        Writes the given value to the file representing it with the specified
        amount of bits.

        Args:
            value (int): the integer value to write to the file
            bits_per_write (int): the amount of bits used for represent the value

        """

        """
        The writing is done using the following logic:

        The given value is byte-shifted starting from the shift
        that makes the value be represented with only one byte.
        e.g. value = 3155 (1100 0101 0011) | bits_per_write = 18
             #1 shift = 18 - 8 = 10
             b = 3155 >> 10 = {0000 0011}

        The successive shifts are 1 byte less then the previous shift
        (until the shift is positive).
        e.g. value = 3155 (1100 0101 0011) | bits_per_write = 18
            #2 shift = 18 - 8 - 8 = 2
            b = 3155 >> 2 = [0011] {0001 0100}

        Notes that only the least significant bits should be taken
        into consideration (for the first shift it is not needed, but
        for successive shifts it is needed in order not to take bits
        outside the byte taken into consideration).

        The first writes just write the obtained number (value >> shift)
        to the file using binary representation.

        After each value write, a certain amount of bits are excluded
        from being written to the file (= unalignment); those will be
        considered for the next write.

        e.g. value = 3155 (1100 0101 0011) | bits_per_write = 18
            ... after 2 shifts ...
            unalignment = 2 (excluded bits)
            unaligned_rest = last_<unalignment>_bits = 11 => 1100 0000

        Next writes will take into account the fact that there might be
        misaligned bits from the previous value and so will adjust the
        shift accordingly.
        Furthermore we have to sum the unaligned_rest from the previous
        value with the first byte obtained from the current value.

        Complete example:
            1) write value 3155 (1100 0101 0011) | bits_per_write = 18

            #1 shift = 18 - 8 = 10
            b = 3155 >> 10 = {0000 0011} => 0 3

            #2 shift = 18 - 8 - 8 = 2
            b = 3155 >> 2 = [0011] {0001 0100} => 1 4

            unalignment = 2
            unaligned_rest = last_<unalignment>_bits = 11 => 1100 0000 => C 0

            2) write value 13 (1101) | bits_per_write = 5

            No shift

            unalignment = 7 (8 - number of left shift in order to let
                            the bits 'touch' the last misaligned bits)
            unaligned_rest  = last_<unalignment>_bits
                            = 1100 0000 |
                              __01 101_
                            = 1101 101_

            3) Close file => write unaligned_rest zero end padded
                1101 101_ => D A

            So => 0 3 1 4 D A
        """

        # self.log("Writing, ", value, " with ", wlength, " bits")

        # The initial shift is the amount of shift needed for make the
        # value exactly of 8 significant bits.
        # The unalignment from the previous write is also taken into consideration.
        shift = bits_per_write - (BYTE_SIZE - self._unalignment)

        # Shifts the value until we have completely considered (and thus shifted) it
        while shift >= 0:

            # Extracts the next 8 bits from the value to write, eventually
            # prepending the unaligned_rest from the previous write
            # The value is put in & with (BYTE_MASK >> unalignment) in order
            # to not consider bits already considered from previous shifts.
            self._B[0] = (value >> shift) \
                         & (BYTE_MASK >> self._unalignment) \
                         | self._unaligned_rest

            # self._log("-> [", "{:x}".format(self._B[0] >> 4), " ", "{:x}".format(self._B[0] & 0xF), "]"
            #           "\t(", value, " >> ", shift, " & ", (BYTE_MASK >> self._unalignment), ")")
            self._file.write(self._B)

            # The next shift will consider the next 8 bits
            shift -= BYTE_SIZE

            # Reset the unalignment, actually needed just for the first shift
            self._unalignment = 0
            self._unaligned_rest = 0

        # We have a certain amount of bits that cannot be written since
        # do not fulfill s full byte
        self._unalignment = shift + BYTE_SIZE

        # Calculated the value of the <unalignment> number of bits we
        # still have not written.
        # The idea is to shift the value so that the least significant bit
        # of the value is a position 'i' so that 'i' + unalignment fulfills a byte.
        # The last | self._unaligned_rest is needed for tolerate cases
        # in which the value to write is not enough to complete a byte
        # (so the value is not written to the file, but instead the unaligned_rest
        # is just increased until we have a full byte to write)
        self._unaligned_rest = (value << (BYTE_SIZE - self._unalignment)) \
            & BYTE_MASK | self._unaligned_rest

        # self._log("unalignment:    ", self._unalignment)
        # self._log("unaligned_rest: ", self._unaligned_rest)

    def close(self):
        """ Closes the file.
        This also writes the last unaligned_rest bits still to write,
        eventually end padded with zeros.
        """

        # self.log("Writing unaligned rest as byte (end padded with zeros)...")
        self._unalignment = 0

        # Note that we can't call __write_byte since it will start pad the byte
        # but we want to end pad it (since this is a bit writing).
        self.write(self._unaligned_rest, BYTE_SIZE)

        self._file.close()


if __name__ == "__main__":
    bw = BitWriter("bit.bin")
    bw.write(297, 12)
    bw.write(11, 5)
    bw.close()

    # br = BitReader("bit.bin")
    # n2 = br.read(12)
    # n2 = br.read(5)
    # br.close()
    #
    # print("Written: ", n)
    # print("Read: ", n2)

