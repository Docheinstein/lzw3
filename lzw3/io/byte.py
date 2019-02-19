from typing import List


class ByteReader:
    """ Entity that provides a way to read a file byte per byte.
    The reading can easily be done by iterate over this entity.
    """

    def __init__(self, in_file_path: str, buffer_size: int = None):
        """ Initializes a new ByteReader for the given file, actually opening it.
        The file will be opened in binary mode, without any encoding assumption.

        Args:
            in_file_path (str): the path of the file that will be read
            buffer_size (int): the size of the buffer to use for reads,
                if not provided the default size will be used.
        """
        if buffer_size is not None:
            self._file = open(in_file_path, "rb", buffering=buffer_size)
        else:
            self._file = open(in_file_path, "rb")

    def __iter__(self):
        """ Returns an iterator for read the file byte per byte.
        Returns:
            this entity as an iterator for read the file byte per byte
        """
        return self

    def __next__(self) -> int:
        """ Reads the next byte from the file.
        The byte is read as it is, without eny encoding assumption.

        Returns:
            int: the next byte read from the file (eventually yields from the
            internal buffer) as integer
        """
        c = self._file.read(1)
        if c:
            return c[0]
        raise StopIteration

    def close(self):
        """ Closes the file. """
        self._file.close()


class ByteWriter:
    """ Entity that provides a way to write raw bytes to a file. """

    def __init__(self, out_file_path: str, buffer_size: int = None):
        """ Initializes a new ByteWriter for the given file, actually opening it.
        The file will be opened in binary mode.

        Args:
            out_file_path (str): the path of the file that will be written
            buffer_size (int): the size of the buffer to use for writes,
                if not provided the default size will be used.
        """
        if buffer_size is not None:
            self._file = open(out_file_path, "wb", buffering=buffer_size)
        else:
            self._file = open(out_file_path, "wb")

    def write(self, values: List[int]):
        """ Writes the given integer values to the file as byte.

        Args:
            values (:obj:`list` of :obj:`int`): list of integer values to write
                as bytes.
        """
        self._file.write(bytearray(values))

    def close(self):
        """ Closes the file. """
        self._file.close()
