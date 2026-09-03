from pathlib import Path
from typing import Any

from .base_parser import SPMBase


class DataParser(SPMBase):
    """Parser for our custom .data files."""

    def __init__(self, file_path: str | Path):
        super().__init__(file_path)

    def parse(self) -> dict[str, Any]:
        raw_data = {}

        # TODO:
        # 1. read .data file
        # 2. extract metadata
        # 3. extract DataFrame columns
        # 4. return flattened dictionary

        return raw_data
