#! /usr/bin/env python3
# -*- coding: utf-8 -*-

##########################################################################
# Copyright (c) 2017 Bertrand Néron. All rights reserved.                #
# Use of this source code is governed by a BSD-style license that can be #
# found in the LICENSE file.                                             #
##########################################################################

import pandas as pd


def norm_voltage(data):
    voltage = data.iloc[:, 1]
    vmin = voltage.min()
    voltage -= vmin
    vmax = voltage.max()
    voltage /= vmax
    return data


def parse_emg(emt_file):
    header = ''
    try:
        for line in emt_file:
            sline = line.strip()
            if sline.startswith('Frame') and 'Time' in sline:
                columns = sline.split('\t')
                break
            else:
                header += line
                continue
    except Exception as err:
        raise RuntimeError('ERROR during parsing of {}: {}'.format(emt_file.name, str(err)))
    data = pd.read_table(emt_file, sep='\t',
                         names=columns,
                         header=None,
                         skip_blank_lines=True,
                         index_col=0,
                         usecols=[0, 1, 2])
    return header, data


def to_file(emt_file, header, data):
    emt_file.write(header)
    data.to_csv(path_or_buf=emt_file,
                sep='\t',
                float_format='%.3f')



