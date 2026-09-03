#!/usr/bin/env python3
"""
Base formatter for Nanonis SPM data.
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
from __future__ import annotations

import numpy as np
from pynxtools_spm.nxformatters.base_formatter import SPMformatter


class NanonisBase(SPMformatter):
    """Base class for Nanonis SPM data formatters."""

    def _arange_axes(self, direction='down'):
        """Arrange fast and slow axes according to the scan direction."""

        fast_slow: list[str]
        if direction.lower() == 'down':
            fast_slow = ['-Y', 'X']
        elif direction.lower() == 'up':
            fast_slow = ['Y', 'X']
        elif direction.lower() == 'right':
            fast_slow = ['X', 'Y']
        elif direction.lower() == 'left':
            fast_slow = ['-X', 'Y']
        else:
            fast_slow = ['X', 'Y']
        self.scan_control.fast_axis = fast_slow[0].lower()
        self.scan_control.slow_axis = fast_slow[1].lower()

        return fast_slow

    def rearrange_data_according_to_axes(self, data, is_forward: bool | None = None):
        """Rearrange array data according to the fast and slow axes.

        (NOTE: This technique is proved for NANONIS data only, for others it may
        not work.)
        Parameters
        ----------
        data : np.ndarray
            Two dimensional array data from scan.
        is_forward : bool, optional
            Default scan direction.
        """

        # if NXcontrol is not defined (e.g. for Bias Spectroscopy)
        if not hasattr(self.scan_control, 'fast_axis') and not hasattr(
            self.scan_control, 'slow_axis'
        ):
            return data
        fast_axis, slow_axis = (
            self.scan_control.fast_axis,
            self.scan_control.slow_axis,
        )

        rearranged = None
        if fast_axis == 'x':
            if slow_axis == '-y':
                rearranged = np.flipud(data)
            rearranged = data
        elif fast_axis == '-x':
            if slow_axis == 'y':
                rearranged = np.fliplr(data)
            elif slow_axis == '-y':
                # np.flip(data)
                np.flip(data)
        elif fast_axis == '-y':
            rearranged = np.flipud(data)
            if slow_axis == '-x':
                rearranged = np.fliplr(rearranged)
        elif fast_axis == 'y':
            rearranged = data
            if slow_axis == '-x':
                rearranged = np.fliplr(rearranged)
        else:
            rearranged = data
        # Consider backward scan
        if is_forward is False:
            rearranged = np.fliplr(rearranged)
        return rearranged
