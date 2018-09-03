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
import matplotlib.pyplot as plt
import colorlog
_log = colorlog.getLogger('emg_analyzer')


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


    def norm_by_track(self, dyn_cal=None):
        """
        Normalize each Voltage records.
        Each record is normalize independently following the formula below.

        .. math::

            zi = xi - min(x) / max(x) - min(x)

        where x=(x1,...,xn) and zi is now your with normalized data.
        """
        new_emg = Emg()
        new_header = self.header.copy()
        new_data = self.data.norm_by_track(self.header.tracks_names, dyn_cal=dyn_cal)
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


    def describe(self):
        """

        :return:
        """
        return self.data.describe()


    def select(self, rest_matrix, coef=1.5):
        """
        select data greater that
        :param rest_matrix:
        :param coef:
        :return:
        """
        new_emg = Emg()
        new_header = self.header.copy()
        new_data, thresholds = self.data.select(rest_matrix, coef=coef)
        new_header.frames = new_data.frames
        new_header.start_time = self.data.start_time
        new_emg.header = new_header
        new_emg.data = new_data
        return new_emg, thresholds


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


    def to_plot(self, out_dir=None, y_scale_auto=False):
        """

        :param out_dir:
        :return:
        """
        figs_path = []
        ymin = self.data.min
        ymax = self.data.max
        for track in self.data.tracks:
            fig_name = "{}_{}.{}".format(self.name, track, 'png')
            transtab = str.maketrans('/ :', '___')
            fig_name = fig_name.translate(transtab)
            _log.info("Compute figure: " + fig_name)
            with plt.style.context('dark_background'):
                plt.close('all')
                fig, ax = plt.subplots()
                width, heigth = fig.get_size_inches()
                fig.set_size_inches([width * 2, heigth])
                x = self.data['Time']
                y = self.data[track]
                ax.plot(x, y,
                        color='red',
                        linewidth=1,
                        label=self.name)
                ax.set(xlabel='time (s)',
                       ylabel='voltage ({})'.format(self.header.unit),
                       title=track)
                if not y_scale_auto:
                    ax.set_ylim([ymin, ymax])

                ax.grid(color='darkgrey', linestyle='--', linewidth=1)
                plt.legend()
                fig_path = os.path.join(out_dir, fig_name)
                fig.savefig(fig_path)
                figs_path.append(fig_path)
            del fig
        return figs_path


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
                self.tracks_names = [c.split(':')[1].split('~')[0].strip() for c in columns]
                if self.tracks_names[0].startswith('Dev1/'):
                    self.tracks_names = [c.replace('Dev1/', '') for c in self.tracks_names]
                break
            else:
                continue
        assert all([v is not None for v in self.__dict__.values()]), \
            "ERROR during parsing '{}': {}".format(emt_file.name,
                                                   ', '.join([k for k, v in self.__dict__.items() if v is None]))
        assert len(self.tracks_names) == self.tracks_nb,\
            "ERROR during parsing '{}': tracks number '{}'" \
            " does not match tracks: {}.".format(emt_file.name,
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
        if self.data.columns[0].upper() == "TIME":
            return list(self.data.columns)[1:]
        else:
            # this is probably the results of a concatanation
            # time was removed because it has no sense
            return list(self.data.columns)

    @property
    def frames(self):
        """

        :return: The number of frames
        :rtype: int
        """
        return len(self.data)


    @property
    def max(self):
        time, data = self._split_data()
        return data.max().max()


    @property
    def min(self):
        time, data = self._split_data()
        return data.min().min()

    @property
    def start_time(self):
        return self.data['Time'][0]


    def _split_data(self):
        """
        :return: split data in 2 DataFrame
                 the first DataFrame contain time and the second one correspond to tracks.
        :rtype: tuple of 2 :class:`pd.DataFrame` object
        """
        if self.data.columns[0].upper() == 'TIME':
            time = self.data.iloc[:, 0:1]
            data = self.data.iloc[:, 1:]
            return time, data
        else:
            raise RuntimeError("The first column is not Time: abort splitting")

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


    def __getitem__(self, track_name):
        """

        :param str track_name:
        :return: return all frames corresponding to the track track_name
        :rtype: :class:`pandas.Serie` object
        """
        return self.data[track_name]


    def get_frames(self, start, stop):
        """

        :param int start:
        :param int stop:
        :return: the frames between start ans stop included
        """
        return self.data.loc[start:stop]


    def norm_by_track(self, tracks_names, dyn_cal=None):
        """
        Compute a new EmgData where each track is normalized
        independently following the formula below
        .. math::

            zi = xi - min(x) / max(x) - min(x)

        where x=(x1,...,xn) and zi is now your matrix with normalized data.

        :param tracks_names: The name of the tracks to normalize.
        :type tracks_names: list of string. each string must match to a data column.
        :param dyn_cal: The min and max for each muscle to normalize
                        The data Frame must have the following structure

                        muscle1   muscle2 muscle3 ...
                    min  0           1.1  ...
                    max 10.1        12.3  ...

        :type dyn_cal: :class:`pandas.DataFrame` object
        :return: a new EmgData
        :rtype: :class:`EmgData` object
        """
        time, data = self._split_data()
        for col in tracks_names:
            track = data[col]
            if dyn_cal is not None:
                v_min = dyn_cal[col]['min']
                v_max = dyn_cal[col]['max']
            else:
                v_min = track.min()
                v_max = track.max()
            _log.debug("vmin = " + str(v_min))
            _log.debug("vmax = " + str(v_max))
            track -= v_min  # do it in place on data frame
            track /= (v_max - v_min)
        data = data.round(decimals=3)
        data = pd.concat([time, data], axis=1)
        return self._new_data(data)


    def norm(self, v_min=None, v_max=None):
        """
        Compute a new EmgData where tracks are normalized following the formula below
        .. math::

            zi = xi - min(x) / max(x) - min(x)

        where x=(x1,...,xn) and zi is now your matrix with normalized data.

        :param float v_min: The min value to use to normalize, if None use the min of the matrix.
        :param float v_max: The max value to use to normalize, if None use the max of the matrix.
        :return: a new EmgData
        :rtype: :class:`EmgData` object
        """
        time, data = self._split_data()
        if v_min is None:
            v_min = data.min().min()
        _log.debug("v_min = " + str(v_min))
        data -= v_min
        if v_max is None:
            v_max = data.max().max()
        _log.debug("v_max = " + str(v_max))
        data /= v_max
        data = data.round(decimals=3)
        data = pd.concat([time, data], axis=1)
        return self._new_data(data)


    def describe(self):
        """
        :return: basic statistics which describe each columns except time.
        :rtype: :class:`pandas.dataFrame` object
        """
        return self.data.iloc[:, 1:].describe()


    def select(self, rest_matrix, coef=1.5):
        """

        :param float threshold:
        :return:
        """
        # split cols
        cols = self.data.columns
        filtered_cols = []
        thresholds = {}
        for col in cols[1:]:
            # The first col should be Time
            c = self.data[col]
            threshold = rest_matrix[col]['mean'] + (rest_matrix[col]['std'] * coef)
            thresholds[col] = threshold
            s = c[c > threshold]
            filtered_cols.append(s)
        new_cols = pd.concat(filtered_cols, axis=1)
        sel_time = self.data['Time']
        new_df = pd.concat([sel_time, new_cols], axis=1)
        return self._new_data(new_df), thresholds


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
                         float_format='%.3f',
                         na_rep='NaN')
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


def desc_summary(sel_summary, index_names=('Experiment', 'Muscle')):
    """

    :param str emg_sel: The path of selection to summarize
    :param index_names:
    :return:
    """
    summaries = []
    for summary_path in sel_summary:
        with open(summary_path) as sel_file:
            header = next(sel_file)
            if not header.startswith('# Summary of activities for condition:'):
                raise RuntimeError("{} is not a selection summary file".format(summary_path))
            mvt = os.path.splitext(os.path.basename(summary_path))[0]
            mvt = mvt.replace('FiltradoRectificado_norm', '')
            summary = pd.read_table(sel_file, comment='#', index_col=0)
        mi = pd.MultiIndex.from_tuples([(mvt, muscle) for muscle in summary.index], names=index_names)
        summary = summary.set_index(mi)
        summaries.append(summary)
    return pd.DataFrame(pd.concat(summaries))
