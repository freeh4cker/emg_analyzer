#! /usr/bin/env python3
# -*- coding: utf-8 -*-

##########################################################################
# Copyright (c) 2017 Bertrand Néron. All rights reserved.                #
# Use of this source code is governed by a BSD-style license that can be #
# found in the LICENSE file.                                             #
##########################################################################

from io import StringIO
import pandas as pd


class Emg:

    def __init__(self):
        self.header = None
        self.data = None


    def parse(self, emt_file):
        self.header = EmgHeader()
        self.header.parse(emt_file)
        self.data = EmgData()
        self.data.parse(emt_file, self.header.muscles)


    def norm(self):
        self.data.norm_voltage(self.header.muscles)
        self.header.unit = "{} Normalized".format(self.header.unit)


    def to_emt(self, emt_file=None):
        buffer = emt_file if emt_file is not None else StringIO()
        self.header.to_tsv(file=buffer)
        self.data.to_tsv(file=buffer)
        if emt_file is None:
            buffer = buffer.getvalue()
        return buffer


    def to_graph(self):
        pass


class EmgHeader:

    _template = """BTS ASCII format

Type:         \t{type}
Measure unit: \t{unit}

Tracks:       \t{tracks}
Frequency:    \t{freq}
Frames:       \t{frames}
Start time:   \t{start_time:.3f}

 Frame\t  Time\t{muscles}\t
"""


    def __init__(self):
        self.type = None
        self.unit = None
        self.tracks = None
        self.freq = None
        self.frames = None
        self.start_time = None
        self.muscles = None


    def parse(self, emt_file):
        for line in emt_file:
            if line.startswith('BTS'):
                pass
            elif line.startswith('Type:'):
                self.type = line.split('\t')[1].strip()
            elif line.startswith('Measure unit:'):
                self.unit = line.split('\t')[1].strip()
            elif line.startswith('Tracks:'):
                self.tracks = int(line.split('\t')[1].strip())
            elif line.startswith('Frequency:'):
                self.freq = line.split('\t')[1].strip()
            elif line.startswith('Frames:'):
                self.frames = int(line.split('\t')[1].strip())
            elif line.startswith('Start time:'):
                self.start_time = float(line.split('\t')[1].strip())
            elif line.startswith(' Frame\t'):
                columns = line.split('\t')
                columns = columns[2:-1]
                self.muscles = [c.replace('Voltage:', '') for c in columns]
                break
            else:
                continue
        assert all([v is not None for v in self.__dict__.values()])


    def to_tsv(self, file=None):
        buffer = file if file is not None else StringIO()
        fields = {k: v for k, v in self.__dict__.items()}
        fields['muscles'] = '\t'.join(['Voltage:{}'.format(m) for m in self.muscles])
        buffer.write(self._template.format(**fields))
        if file is None:
            buffer = buffer.getvalue()
        return buffer


class EmgData:

    def __init__(self):
        self.data = None

    def parse(self, emt_file, columns):
        columns = ['Frame', 'Time'] + columns
        self.data = pd.read_table(emt_file,
                                  sep='\t',
                                  names=columns,
                                  header=None,
                                  skip_blank_lines=True,
                                  index_col=0,
                                  usecols=list(range(len(columns)))
                                  )


    def norm_voltage(self, muscles):
        for col in muscles:
            voltage = self.data[col]
            v_min = voltage.min()
            voltage -= v_min  # do it in place on data frame
            v_max = voltage.max()
            voltage /= v_max


    def to_tsv(self, file=None, header=False):
        buffer = file if file is not None else StringIO()
        self.data.to_csv(path_or_buf=buffer,
                         header=header,
                         sep='\t',
                         float_format='%.3f')
        if file is None:
            buffer = buffer.getvalue()
        return buffer
