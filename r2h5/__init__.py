# r2h5/__init__.py

__version__ = "1.2"

import logging

# ANSI color codes
COLOR_RESET = "\033[0m"
BOLD = "\033[1m"
COLOR_MAP = {
    'DEBUG': '',
    'INFO': "\033[32m",     # Green
    'WARNING': "\033[33m",  # Orange/Yellow
    'ERROR': "\033[31m",    # Red
}

class FullLineColorFormatter(logging.Formatter):
    def format(self, record):
        level = f"[{record.levelname:<5}]"
        time = self.formatTime(record, self.datefmt)
        message = record.getMessage()

        bold_parts = f"{BOLD}[{time}] {level} {record.module}::{record.funcName}:{COLOR_RESET}"
        color = COLOR_MAP.get(record.levelname, "")
        return f"{color}{bold_parts} {message}{COLOR_RESET}"

def setup_logging(level=logging.INFO):
    handler = logging.StreamHandler()
    handler.setFormatter(FullLineColorFormatter(datefmt='%H:%M:%S'))
    logging.basicConfig(level=level, handlers=[handler])

from .config_parser import load_yaml_config
from .converter import DatasetConverter
from .batch import get_slurm_script
from .type import get_dtype, convert_rvec_to_numpy, fix_array_size, fix_array_size_and_create_valid
from .rdf_defines import super_ntuples

# Save absolute path of the package (this file up 1 directory)
import os
__package_path__ = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


