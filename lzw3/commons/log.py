from abc import ABC, abstractmethod
from datetime import datetime


class Logger:
    """ Provides a unique point for print statements.
    This may be useful for enable/disable print statements
    for the whole application.
    """

    _enabled = True
    """ Whether the logger is enabled. """

    @staticmethod
    def log(tag: str, *args):
        """ Prints to argument list to standard output using the given tag.

        Args:
            tag (str): tag of the entity that produced the message
            *args: args to yield to the print statement
        """
        if Logger._enabled:
            print("[" + datetime.now().strftime("%H:%M:%S") + "] {" + tag + "} ", *args, sep='')

    @staticmethod
    def enable_logger(enable: bool):
        """ Enables or disable the logger for the whole application.

        Args:
            enable (bool): whether enable the logger for the whole application
        """
        Logger._enabled = enable

    @staticmethod
    def is_logger_enabled() -> bool:
        """ Returns whether the logger is enabled for the whole application.

        Returns:
            bool: whether the logger is enabled for the whole application
        """
        return Logger._enabled


class Loggable(ABC):
    """ Represents an entity which might be able to print log statements."""

    def _log(self, *args):
        """ Prints to argument list to standard output.
        The tag provided by get_logger_name() is prepended
        to the print statement.

        Args:
            *args: args to yield to the print statement
        """
        if self.enabled:
            Logger.log(self.tag, *args)

    def __init__(self):
        # Cache the values of is_logger_enabled() and get_logger_name()
        # in order to not call these functions for each print statement.
        self.enabled = self._can_log()
        self.tag = self._get_logger_tag()

    @abstractmethod
    def _get_logger_tag(self) -> str:
        """
        Returns the tag that should be prepended to the print statements
        done by this entity.
        Must be implemented by entities that inherit from this class.

        Returns:
            str: the tag to prepend to print statements from this entity
        """
        pass

    @abstractmethod
    def _can_log(self) -> bool:
        """
        Returns whether this entity should actually print to standard
        output.
        Must be implemented by entities that inherit from this class.

        Returns:
            bool: whether enable logging for this entity
        """
        pass
