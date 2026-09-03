"""
A short description on STS reader which also suitable for file from STM .
"""

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

import copy
from typing import Any

import numpy as np
import yaml
from pynxtools import get_nexus_version
from pynxtools.dataconverter.readers.base.reader import BaseReader
from pynxtools.dataconverter.template import Template
from pynxtools_spm.nxformatters.base_formatter import SPMformatter

# For flattened key-value pair from nested dict.
REPLACE_NESTED: dict[str, str] = {}


def manually_filter_data_type(template):
    """Check for the data with key type and fix it"""
    nexus_key_to_dt = {
        '/ENTRY[entry]/INSTRUMENT[instrument]/ENVIRONMENT[environment]/current_sensor/current_gain': float,
        'rcs_fabrication/model': str,
        'hardware/mode': str,
        'hardware/model/@version': str,
    }
    template_copy = copy.deepcopy(template)
    for key, val in template_copy.items():
        for manual_key, dt in nexus_key_to_dt.items():
            if key.endswith(manual_key):
                try:
                    template[key] = dt(val)
                except (ValueError, TypeError):
                    print(
                        f'Warning: Could not convert data {val} for field {key} to {dt}'
                    )
                    del template[key]


# pylint: disable=invalid-name, too-few-public-methods
class SPMReader(BaseReader):
    """Reader for XPS."""

    supported_nxdls = ['NXspm', 'NXsts', 'NXstm', 'NXafm']

    def read(
        self,
        template: dict = None,
        file_paths: tuple[str] = None,
        objects: tuple[Any] = None,
    ):
        """
        General read method to prepare the template.
        """
        filled_template: dict | None = Template()
        eln_file: str = None
        config_file: str | None = None
        data_file: str | None = ''
        experiment_technique: str | None = None
        raw_file_ext: str | None = None
        auxiliary_files: list[str] = []

        for file in file_paths:
            # Vendors do not agree on the case of the extension, e.g. Bruker
            # writes '.FLT'.
            ext = file.rsplit('.', 1)[-1].lower()
            fl_obj: object
            if ext in ['sxm', 'data']:
                data_file = file
                raw_file_ext = ext
            if ext == 'json':
                config_file = file
            if ext in ['yaml', 'yml']:
                eln_file = file
                with open(file, encoding='utf-8') as fl_obj:
                    eln_dict = yaml.safe_load(fl_obj)
                    experiment_technique = eln_dict.get('experiment_technique')
                    # TODO get definition name
                if experiment_technique is None:
                    raise ValueError('Experiment technique is not defined in ELN file.')
            else:
                auxiliary_files.append(file)
        raw_file_ext = raw_file_ext.lower() if raw_file_ext else None
        if not eln_file:
            raise ValueError('ELN file is required for the reader to work.')
        if not data_file:
            raise ValueError('Data file is required for the reader to work.')

        formatter_obj: SPMformatter | None = None
        # Get callable object that has parser inside
        if experiment_technique == 'STM' and raw_file_ext == 'sxm':
            from pynxtools_spm.nxformatters.nanonis.nanonis_sxm_stm import (
                NanonisSxmSTM,
            )

            formatter_obj = NanonisSxmSTM(
                template=template,
                raw_file=data_file,
                eln_file=eln_file,
                config_file=config_file,
            )
            # nss.get_nxformatted_template()
        elif experiment_technique == 'AFM':
            if raw_file_ext == 'sxm':
                from pynxtools_spm.nxformatters.nanonis.nanonis_sxm_afm import (
                    NanonisSxmAFM,
                )

                formatter_obj = NanonisSxmAFM(
                    template=template,
                    raw_file=data_file,
                    eln_file=eln_file,
                    config_file=config_file,
                )
        elif experiment_technique == 'BiasSpectroscopy' and raw_file_ext == 'data':
            from myfirstplugin.nxformatters.nanonis.data_BiasSpectr import (
                DataBiasSpectroscopy,
            )

            formatter_obj = DataBiasSpectroscopy(
                template=template,
                raw_file=data_file,
                eln_file=eln_file,
                config_file=config_file,
            )
        # elif experiment_technique == 'STS' and raw_file_ext == 'dat':
        #     from pynxtools_spm.nxformatters.nanonis.nanonis_dat_sts import NanonisDatSTS

        #     formatter_obj = NanonisDatSTS(
        #         template=template,
        #         raw_file=data_file,
        #         eln_file=eln_file,
        #         config_file=config_file,
        #     )
        #     # nds.get_nxformatted_template()

        if not formatter_obj:
            raise ValueError(
                f'IncorrectExperiment: Incorrect experiment technique ({experiment_technique}) or file extension ({raw_file_ext}) are given'
            )
        formatter_obj.get_nxformatted_template()
        # manually_remove the empty data
        for key, val in template.items():
            if isinstance(val, np.ndarray):
                filled_template[key] = val
                continue
            elif val in (None, ''):
                continue

            filled_template[key] = val
        # Set nexus def version
        filled_template['/ENTRY[entry]/definition/@version'] = get_nexus_version()
        if not filled_template.keys():
            raise ValueError(
                'Reader could not read anything! Check for input files and the'
                ' corresponding extension.'
            )
        manually_filter_data_type(filled_template)
        return filled_template


READER = SPMReader
