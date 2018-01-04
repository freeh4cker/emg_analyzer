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
    """
    Class to handle **E**\ lectro **M**\ yo **G**\ ram.
    From *.emt* files.
    """

    def __init__(self):
        """
        Initialization of Emg object.
        """
        self.header = None
        self.data = None


    def parse(self, emt_file):
        """
        Parse emt_file to fill this object.

        :param emt_file: the file to parse
        :type emt_file: file object
        """
        self.header = EmgHeader()
        self.header.parse(emt_file)
        self.data = EmgData()
        self.data.parse(emt_file, self.header.tracks_names)


    def norm(self):
        """
        Normalize each Voltage records.
        Each record is normalize independently following the formula below.

        .. math::

            zi = xi - min(x) / max(x) - min(x)

        where x=(x1,...,xn) and zi is now your with normalized data.
        """
        self.data.norm_tracks(self.header.tracks_names)


    def to_emt(self, emt_file=None):
        """
        Write the emg in .emt file format

        :param emt_file: Optional buffer to write to.
                        If None is provided the result is returned as a string.
        :type emt_file: StringIO-like or file-like object.
        :returns: The emg formatted to *'.emt'* format
        :rtype: file-like object or string
        """
        buffer = emt_file if emt_file is not None else StringIO()
        self.header.to_tsv(file=buffer)
        self.data.to_tsv(file=buffer)
        if emt_file is None:
            buffer = buffer.getvalue()
        return buffer


    def to_graph(self):
        pass


class EmgHeader:
    """
    Class to handle the header of an *.emt* file
    """

    _template = """BTS ASCII format

Type:         \t{type}
Measure unit: \t{unit}

Tracks:       \t{tracks_nb}
Frequency:    \t{freq}
Frames:       \t{frames}
Start time:   \t{start_time:.3f}

 Frame\t  Time\t{tracks_names}\t
"""

    def __init__(self):
        """
        Initialization of EmgHeader object
        """
        self.type = None
        self.unit = None
        self.tracks_nb = None
        self.freq = None
        self.frames = None
        self.start_time = None
        self.tracks_names = None


    def __eq__(self, other):
        for attr, val in self.__dict__.items():
            if getattr(other, attr) != val:
                return False
        return True


    def parse(self, emt_file):
        """
        Parse emt_file to fill this object

        :param emt_file: the file to parse
        :type emt_file: file object
        """
        for line in emt_file:
            if line.startswith('BTS'):
                pass
            elif line.startswith('Type:'):
                self.type = line.split('\t')[1].strip()
            elif line.startswith('Measure unit:'):
                self.unit = line.split('\t')[1].strip()
            elif line.startswith('Tracks:'):
                self.tracks_nb = int(line.split('\t')[1].strip())
            elif line.startswith('Frequency:'):
                self.freq = line.split('\t')[1].strip()
            elif line.startswith('Frames:'):
                self.frames = int(line.split('\t')[1].strip())
            elif line.startswith('Start time:'):
                self.start_time = float(line.split('\t')[1].strip())
            elif line.startswith(' Frame\t'):
                columns = line.split('\t')
                columns = columns[2:-1]
                self.tracks_names = [c.replace('Voltage:', '') for c in columns]
                break
            else:
                continue
        assert all([v is not None for v in self.__dict__.values()]), \
            "ERROR during parsing '{}': {}".format(emt_file.name,
                                                    ', '.join([k for k, v in self.__dict__.items() if v is None]))
        assert len(self.tracks_names) == self.tracks_nb, \
            "ERROR during parsing '{}': tracks number does not match tracks.".format(emt_file.name)



    def to_tsv(self, file=None):
        """
        Write this header in tsv according the *.emt* file format

        :param file: Optional buffer to write to.
                    If None is provided the result is returned as a string.
        :type file: StringIO-like or file-like object.
        :returns: The header formatted into *'.emt'* format
        :rtype: file-like object or string
        """
        buffer = file if file is not None else StringIO()
        fields = {k: v for k, v in self.__dict__.items()}
        fields['tracks_names'] = '\t'.join(['Voltage:{}'.format(m) for m in self.tracks_names])
        buffer.write(self._template.format(**fields))
        if file is None:
            buffer = buffer.getvalue()
        return buffer


class EmgData:
    """
    Class to handle the data of an *.emt* file
    """

    def __init__(self):
        """
        Initialization of EmgData object.
        """
        self.data = None


    def parse(self, emt_file, tracks):
        """
        Parse emt_file to fill this object.

        :param emt_file: the file to parse
        :type emt_file: file object
        :param tracks: The list of the tracks to parse.
        :type tracks: List of string
        """
        columns = ['Frame', 'Time'] + tracks
        self.data = pd.read_table(emt_file,
                                  sep='\t',
                                  names=columns,
                                  header=None,
                                  skip_blank_lines=True,
                                  index_col=0,
                                  usecols=list(range(len(columns)))
                                  )

    @property
    def tracks(self):
        """
        :return: The list of the tracks in this EMG.
        :rtype: List of string
        """
        return list(self.data.columns)[1:]


    def norm_tracks(self, tracks_names):
        """
        Normalize records corresponding to *tracks*.
        Each record is normalize independently following the formula below
        .. math::

            zi = xi - min(x) / max(x) - min(x)

        where x=(x1,...,xn) and zi is now your with normalized data.

        :param tracks_names: The name of the tracks to normalize.
        :type tracks_names: list of string. each string must match to a data column.
        """
        for col in tracks_names:
            track = self.data[col]
            v_min = track.min()
            track -= v_min  # do it in place on data frame
            v_max = track.max()
            track /= v_max
        self.data = self.data.round({t: 3 for t in self.tracks})



    def to_tsv(self, file=None, header=False):
        """
        Write this data in tsv according the *.emt* file format

        :param file: Optional buffer to write to.
                    If None is provided the result is returned as a string.
        :type file: StringIO-like or file-like object.
        :param header: boolean or list of string, default False
                       Write out the column names.
                       If a list of strings is given it is assumed
                       to be aliases for the column names.
        :type header: boolean
        :returns: The header formatted into *'.emt'* format
        :rtype: file-like object or string
        """
        buffer = file if file is not None else StringIO()
        self.data.to_csv(path_or_buf=buffer,
                         header=header,
                         sep='\t',
                         float_format='%.3f')
        if file is None:
            buffer = buffer.getvalue()
        return buffer
