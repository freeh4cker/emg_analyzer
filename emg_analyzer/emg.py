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
#     _header = """BTS ASCII format
#
# Type:         \tEmg tracks
# Measure unit: \tV
#
# Tracks:       \t1
# Frequency:    \t1000 Hz
# Frames:       \t33780
# Start time:   \t0.000
#
#  Frame\t  Time\tVoltage:LDA~2\t
# """

    header_template = """BTS ASCII format

Type:         \t{type}
Measure unit: \tV

Tracks:       \t{tracks}
Frequency:    \t{freq}
Frames:       \t{frames}
Start time:   \t{time}

 Frame\t  Time\t{voltage}\t
"""


    def parse_header(emt_file):
        vars = {}
        for line in emt_file:
            if line.startswith('BTS'):
                pass
            elif line.startswith('Type:'):
                vars['type'] = line.split('\t')[1].strip()
            elif line.startswith('Measure:'):
                vars['measure'] = line.split('\t')[1].strip()
            elif line.startswith('Tracks:'):
                vars['tracks'] = line.split('\t')[1].strip()
            elif line.startswith('Frequency:'):
                vars['freq'] = line.split('\t')[1].strip()
            elif line.startswith('Frames:'):
                vars['frames'] = line.split('\t')[1].strip()
            elif line.startswith('Start time:'):
                vars['time'] = line.split('\t')[1].strip()
            elif line.startswith(' Frame\t'):
                columns = line.split('\t')
                vars['voltage'] = columns[-2]
                break
            else:
                continue
        header = header_template.format(**vars)
        return header, columns

    def parse_data(emt_file, columns):
        data = pd.read_table(emt_file, sep='\t',
                             names=columns,
                             header=None,
                             skip_blank_lines=True,
                             index_col=0,
                             usecols=[0, 1, 2])
        return data

    try:
        header, columns = parse_header(emt_file)
        data = parse_data(emt_file, columns)
    except Exception as err:
        raise RuntimeError('ERROR during parsing of {}: {}'.format(emt_file.name, str(err)))

    return header, data


def to_file(emt_file, header, data):
    emt_file.write(header)
    data.to_csv(path_or_buf=emt_file,
                header=False,
                sep='\t',
                float_format='%.3f')



