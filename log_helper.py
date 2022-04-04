import logging


class Color:
    """A class for terminal color codes."""

    BOLD = "\033[1m"
    BLUE = "\033[94m"
    WHITE = "\033[97m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    YELLOW_BG = "\033[43;1m"
    RED = "\033[91m"
    BOLD_WHITE = BOLD + WHITE
    BOLD_BLUE = BOLD + BLUE
    BOLD_GREEN = BOLD + GREEN
    BOLD_YELLOW = BOLD + YELLOW
    BOLD_RED = BOLD + RED
    END = "\033[0m"


class ColorLogFormatter(logging.Formatter):
    """A class for formatting colored logs."""

    # FORMAT = "%(prefix)s%(msg)s%(suffix)s"
    FORMAT = '%(prefix)s@%(lineno)-3d: %(levelname)-8s %(message)s%(suffix)s'

    LOG_LEVEL_COLOR = {
        "DEBUG": {'prefix': Color.BLUE, 'suffix': Color.END},
        "INFO": {'prefix': Color.BOLD_BLUE, 'suffix': Color.END},
        "WARNING": {'prefix': Color.YELLOW_BG, 'suffix': Color.END},
        "ERROR": {'prefix': Color.RED, 'suffix': Color.END},
        "CRITICAL": {'prefix': Color.BOLD_RED, 'suffix': Color.END},
    }

    def format(self, record):
        """Format log records with a default prefix and suffix to terminal color codes that corresponds to the log level name."""
        if not hasattr(record, 'prefix'):
            record.prefix = self.LOG_LEVEL_COLOR.get(record.levelname.upper()).get('prefix')

        if not hasattr(record, 'suffix'):
            record.suffix = self.LOG_LEVEL_COLOR.get(record.levelname.upper()).get('suffix')

        formatter = logging.Formatter(self.FORMAT)
        return formatter.format(record)
