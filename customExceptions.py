"""
This module add game-specific exceptions
"""


class Error(Exception):
    """ Base class for the rest of the exceptions """


class NotEnoughBalance(Error):
    """ Exception that will be raised when a player tries to bet more than his current balance """


class BelowMinBet(Error):
    """ Exception that will be raised when a player tries to bet less than the table's minimum """
