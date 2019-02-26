import os
from abc import ABC, abstractmethod
from typing import List

from lzw3.commons.log import Loggable, Logger
from lzw3.res.utils import read_textual_resource


class LZWHelper(Loggable, ABC):
    """
    Provides commons methods for invoke a LZW utility (compressor or decompressor),
    eventually on directories in a recursive manner.
    """

    def __init__(self, recursive: bool, verbose: bool,
                 time: bool, keep: bool, force: bool):
        """ Initializes this helper.

        Args:
            recursive (bool): whether directories should be entered recursively
            verbose (bool): whether output basic info to standard output
            time (bool): whether print the time of each task executed
                        (is taken into consideration only if verbose is true)
            keep (bool): whether keep original files after the task
            force (bool): whether force the action (for compression means to
                            always keep the output file)
        """
        super().__init__()
        self._recursive = recursive
        self._verbose = verbose
        self._time = time
        self._keep = keep
        self._force = force

    def handle(self, files: List[str]):
        """ Handles the file list using the settings provided to this helper.

        Args:
            files (:obj:`list` of :obj:`str`): list of files (or directories)
                to handle
        """
        for f in files:
            if os.path.isfile(f):
                self._handle_file(f)
            elif os.path.isdir(f):
                if self._recursive:
                    self._handle_directory(f)
                else:
                    self._log("Found a directory while mode is non-recursive; skipping it")
            # os.path.isX(f) return False if the f doesn't exist
            else:
                self._log("File '", f, "' doesn't exist; skipping it")
                self._print("'", f, "' not found!")

    def _handle_directory(self, directory: str):
        """ Handles the given directory using the settings provided to this helper.

        Args:
            directory (str): the path of the directory to handle
        """
        for root, d_names, f_names in os.walk(directory):
            self._log("Visiting ", directory, "\n"
                      "\troot:  ", root, "\n"
                      "\tdirs:  ", d_names, "\n"
                      "\tfiles:  ", f_names)
            for f in f_names:
                self._handle_file(os.path.join(root, f))

    @abstractmethod
    def _handle_file(self, file: str):
        """ Handles the (regular) file by executing the appropriate task.
        Actually it should be implemented compressing xor decompressing the file.

        Args:
            file (str): the path of the file to handle
        """
        pass

    def _print(self, *args, **kwargs):
        """ Prints the standard output only if the verbose flag has been set.

        Args:
            *args: the arguments to pass to print
            **kwargs: the keyword arguments to pass to print
        """
        if self._verbose:
            print(*args, **kwargs, sep="")


class LZWHelperStarter:
    """ Parses an argument list and start the LZWHelper with the arguments found. """

    # Acceptable and known arguments

    ARG_RECURSIVE = "-r"
    ARG_VERBOSE = "-v"
    ARG_TIME = "-t"
    ARG_KEEP = "-k"
    ARG_FORCE = "-f"
    ARG_DEBUG = "-d"

    def __init__(self, helper_class: type(LZWHelper), help_res: str):
        """
        Initializes this starter and bounds it to the given helper class
        and help resource.

        Args:
            helper_class (type): the class of the LZWHelper to invoke
            help_res (str): the name of the resource that will be used as help page
        """
        self._helper_class = helper_class
        self._help_resource = help_res

    def start(self, args: List[str]):
        """ Parses the given argument list and actually start the bound LZWHelper.
        Accepted arguments are "-r", "-v", "-t", "-k", "-f", "-d".

        Args:
            args (:obj:`list` of :obj:`str`): the argument list (sys.argv)
        """
        arg_count = len(args)

        # Quit showing help if the user doesn't provide arguments
        if arg_count == 0:
            self._abort(-1, True)

        recursive = False
        verbose = False
        time = False
        keep = False
        force = False
        debug = False
        files = []

        # Whether the next arguments will be treated as file names
        reading_files_args = False

        # Parse the arguments;
        # The first time an argument without a leading dash is encountered
        # it will be considered as a file (and thus all the successive arguments).
        # So all the dash arguments must appear before the file list.
        for arg in args:

            if not arg.startswith("-"):
                reading_files_args = True

            if reading_files_args:
                files.append(arg)
            else:
                recursive |= (arg == LZWHelperStarter.ARG_RECURSIVE)
                verbose |= (arg == LZWHelperStarter.ARG_VERBOSE)
                time |= (arg == LZWHelperStarter.ARG_TIME)
                keep |= (arg == LZWHelperStarter.ARG_KEEP)
                force |= (arg == LZWHelperStarter.ARG_FORCE)
                debug |= (arg == LZWHelperStarter.ARG_DEBUG)

        Logger.enable_logger(debug)
        Logger.log("MAIN", "Executing LZW task with following options:\n",
                   "\trecursive:  ", recursive, "\n",
                   "\tverbose:    ", verbose, "\n",
                   "\ttime:       ", time, "\n",
                   "\tkeep:       ", keep, "\n",
                   "\tforce:      ", force, "\n",
                   "\tdebug:      ", debug, "\n",
                   "\tfiles:      ", files)

        self._helper_class(recursive=recursive, verbose=verbose,
                           time=time, keep=keep, force=force).handle(files)

    def _abort(self, exit_code: int, show_help: bool):
        """ Quits with the given exit code, eventually showing an help page.

        Args:
            exit_code (int): the program exit code
            show_help (bool): whether show the help page before quit
        """
        if show_help:
            print(read_textual_resource(self._help_resource))
        exit(exit_code)
