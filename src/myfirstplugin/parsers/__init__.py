# from nomad.config.models.plugins import ParserEntryPoint
# from pydantic import Field


# class NewParserEntryPoint(ParserEntryPoint):
#     parameter: int = Field(0, description='Custom configuration parameter')

#     def load(self):
#         from myfirstplugin.parsers.parser import NewParser

#         return NewParser(**self.model_dump())


# parser_entry_point = NewParserEntryPoint(
#     name='NewParser',
#     description='New parser entry point configuration.',
#     mainfile_name_re=r'.*\.newmainfilename',
# )

#!/usr/bin/env python3
"""
Choose the appropriate parser based on the file extension and the ELN data.
"""
# -*- coding: utf-8 -*-
#
# Copyright The NOMAD Authors.
#
# This file is part of NOMAD. See https://nomad-lab.eu for further info.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

import logging
import os
from collections.abc import Callable, Iterable
from pathlib import Path, PosixPath
from typing import Any, Union

import pynxtools_spm.parsers.helpers as phs
from pynxtools_spm.parsers.spaik_data import DataParser

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG, format='%(levelname)s - %(message)s')


class SPMParser:
    """Select and run the parser for supported raw-data files."""

    _parsers = {
        'data': DataParser,
    }

    def get_raw_data_dict(
        self,
        file: str | Path,
        eln: dict | None = None,
        file_ext: str | None = None,
    ) -> dict[str, Any]:
        """
        Parse a raw data file and return the flattened raw-data dictionary.

        Parameters
        ----------
        file
            Path to the raw data file.
        eln
            Currently unused. Kept for compatibility with the formatter API.
        file_ext
            Optional explicit file extension.
        """

        if file_ext is None:
            file_ext = Path(file).suffix.lstrip('.')

        file_ext = file_ext.lower()

        try:
            parser_class = self._parsers[file_ext]
        except KeyError as exc:
            raise ValueError(
                f"Unsupported file extension '.{file_ext}'. "
                f'Supported extensions: {list(self._parsers)}'
            ) from exc

        parser = parser_class(file)
        return parser.parse()

    def parse(self, file: str | Path) -> dict[str, Any]:
        """Convenience wrapper."""
        return self.get_raw_data_dict(file)
