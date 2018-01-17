#! /usr/bin/env python3
# -*- coding: utf-8 -*-

##########################################################################
# Copyright (c) 2017-2018 Bertrand Néron. All rights reserved.           #
# Use of this source code is governed by a BSD-style license that can be #
# found in the LICENSE file.                                             #
##########################################################################

import os
from io import StringIO
import numpy as np
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
        self.name = None
        self.header = None
        self.data = None


    def __eq__(self, other):
        """

        :param other:
        :return:
        """
        return self.header == other.header and self.data == other.data


    def parse(self, emt_file):
        """
        Parse emt_file to fill this object.

        :param emt_file: the file to parse
        :type emt_file: file object
        """
        self.name = os.path.splitext(os.path.basename(emt_file.name))[0]
        self.header = EmgHeader()
        self.header.parse(emt_file)
        self.data = EmgData()
        self.data.parse(emt_file, self.header.tracks_names)
        if self.header.frames != self.data.frames:
            raise RuntimeError("The number of Frames in header '{}' "
                               "does not match data frames '{}'.".format(self.header.frames,
                                                                       self.data.frames))


    def norm_by_track(self):
        """
        Normalize each Voltage records.
        Each record is normalize independently following the formula below.

        .. math::

            zi = xi - min(x) / max(x) - min(x)

        where x=(x1,...,xn) and zi is now your with normalized data.
        """
        new_emg = Emg()
        new_header = self.header.copy()
        new_data = self.data.norm_by_track(self.header.tracks_names)
        new_emg.header = new_header
        new_emg.data = new_data
        return new_emg


    def norm(self):
        """
        Compute a new Emg where tracks are normalized (all together) following the formula below
        .. math::

            zi = xi - min(x) / max(x) - min(x)

        where x=(x1,...,xn) and zi is now your matrix with normalized data.

        :return: a new Emg
        :rtype: :class:`Emg` object
        """
        new_emg = Emg()
        new_header = self.header.copy()
        new_data = self.data.norm()
        new_emg.header = new_header
        new_emg.data = new_data
        return new_emg


    def group_by_track(self, emg_list):
        merge = {}
        emg_list.insert(0, self)
        for emg in emg_list:
            for track in emg.header.tracks_names:
                if track in merge:
                    merge[track].append(emg)
                else:
                    merge[track] = [emg]
        merged_emg = []
        for new_emg_name in merge:
            new_emg = Emg()
            new_emg.name = new_emg_name
            new_emg.header = self.header.copy()
            new_emg.header.tracks_nb = len(merge[new_emg_name])
            emg_2_group = {emg.name: emg.data for emg in merge[new_emg_name]}
            new_emg.data = EmgData.group_track(new_emg_name, emg_2_group)
            new_emg.header.tracks_names = new_emg.data.tracks
            new_emg.header.frames = new_emg.data.frames
            merged_emg.append(new_emg)
        return merged_emg



    def to_emt(self, file=None):
        """
        Write the emg in .emt file format

        :param file: Optional buffer to write to.
                     If None is provided the result is returned as a string.
        :type file: StringIO-like or file-like object.
        :returns: The emg formatted to *'.emt'* format
        :rtype: file-like object or string
        """
        buffer = file if file is not None else StringIO()
        self.header.to_tsv(file=buffer)
        self.data.to_tsv(file=buffer)
        if file is None:
            buffer = buffer.getvalue()
        return buffer


    def to_plot(self):
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


    def copy(self):
        """
        :return: a deep copy of the header
        :rtype: a :class:`EmgHeader` object.
        """
        new_header = EmgHeader()
        for attr, value in self.__dict__.items():
            setattr(new_header, attr, value)
        return new_header


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
                columns = line.strip().split('\t')
                columns = columns[2:]
                self.tracks_names = [c.replace('Voltage:', '') for c in columns]
                break
            else:
                continue
        assert all([v is not None for v in self.__dict__.values()]), \
            "ERROR during parsing '{}': {}".format(emt_file.name,
                                                    ', '.join([k for k, v in self.__dict__.items() if v is None]))
        assert len(self.tracks_names) == self.tracks_nb, \
            "ERROR during parsing '{}': tracks number '{}' does not match tracks: {}.".format(emt_file.name,
                                                                                              self.tracks_nb,
                                                                                              ", ".join(self.tracks_names))



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

    def __eq__(self, other):
        if other.data.shape != self.data.shape:
            return False
        if all(other.data.columns == self.data.columns):
            return np.isclose(self.data, other.data).all()
        else:
            return False


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


    @property
    def frames(self):
        """

        :return: The number of frames
        :rtype: int
        """
        return len(self.data)


    def _split_data(self):
        """
        :return: split data in 2 DataFrame
                 the first DataFrame contain time and the second one correspond to tracks.
        :rtype: tuple of 2 :class:`pd.DataFrame` object
        """
        time = self.data.iloc[:, 0:1]
        data = self.data.iloc[:, 1:]
        return time, data

    @staticmethod
    def _new_data(data):
        """
        :param data: DataFrame to put in EmgData
        :type data: :class:`pd.DataFrame` object
        :return: new EmgData
        :rtype: :class:`pd.DataFrame` object
        """
        new_data = EmgData()
        new_data.data = data
        return new_data


    def norm_by_track(self, tracks_names):
        """
        Compute a new EmgData where each track is normalized
        independently following the formula below
        .. math::

            zi = xi - min(x) / max(x) - min(x)

        where x=(x1,...,xn) and zi is now your matrix with normalized data.

        :param tracks_names: The name of the tracks to normalize.
        :type tracks_names: list of string. each string must match to a data column.
        :return: a new EmgData
        :rtype: :class:`EmgData` object
        """
        time, data = self._split_data()
        for col in tracks_names:
            track = data[col]
            v_min = track.min()
            track -= v_min  # do it in place on data frame
            v_max = track.max()
            track /= v_max
        data = data.round(decimals=3)
        data = pd.concat([time, data], axis=1)
        return self._new_data(data)


    def norm(self):
        """
        Compute a new EmgData where tracks are normalized following the formula below
        .. math::

            zi = xi - min(x) / max(x) - min(x)

        where x=(x1,...,xn) and zi is now your matrix with normalized data.

        :param tracks_names: The name of the tracks to normalize.
        :type tracks_names: list of string. each string must match to a data column.
        :return: a new EmgData
        :rtype: :class:`EmgData` object
        """

        time, data = self._split_data()
        v_min = data.min().min()
        data -= v_min
        v_max = data.max().max()
        data /= v_max
        data = data.round(decimals=3)
        data = pd.concat([time, data], axis=1)
        return self._new_data(data)


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


    @staticmethod
    def group_track(track, emg_2_group):
        """

        :param emg_2_group: the data where to extract track and merge
        :param track: dict {'name': EmgData}
        :return: new EmgData where all tracks come from
                 EmgData emg_2_group in named 'track' ::

                 exp1: Frame Time A  B
                        0     0   1 10
                        1     1   2 20
                        2     2   3 30

                 exp2: Frame Time  A    B
                        0     0   1.2 10.2
                        1     1   2.2 20.2
                        2     2   3.2 30.2

                A:    Frame Time  exp1  exp2
                        0     0    1    1.2
                        1     1    2    2.2
                        2     2    3    3.2

        :rtype: :class:`EmgData` object
        """
        one_emg = next(iter(emg_2_group.values()))
        data = one_emg.data['Time']
        series = []
        for name, emg in emg_2_group.items():
            # s is a pandas.Serie
            s = emg.data[track]
            s.name = name
            series.append(s)
        series.insert(0, data)
        data = pd.concat(series, axis=1)
        return EmgData._new_data(data)
