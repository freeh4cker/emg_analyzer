##########################################################################
# Copyright (c) 2017-2018 Bertrand Néron. All rights reserved.           #
# Use of this source code is governed by a BSD-style license that can be #
# found in the LICENSE file.                                             #
##########################################################################


import io
import pandas as pd

try:
    from tests import EmgTest
except ImportError as err:
    msg = "Cannot import emg_analyzer: {0!s}".format(err)
    raise ImportError(msg)

from emg_analyzer.emg import EmgData


class TestEmgData(EmgTest):

    def test_parse_one_track(self):
        columns = ['Frame', 'Time', 'A']
        data_expected = pd.DataFrame([[i, i/1000, (i*10)+10] for i in range(10)], columns=columns)
        data_expected = data_expected.astype(dtype={'Frame': 'int', 'Time': 'float', 'A': 'float'})
        data_expected = data_expected.set_index('Frame')
        data_received = EmgData()
        data_path = self.get_data('data_one_track.emt')
        with open(data_path) as data_file:
            data_received.parse(data_file, columns[2:])
        pd.util.testing.assert_frame_equal(data_expected, data_received.data)


    def test_parse_several_tracks(self):
        data = {'Frame': [i for i in range(10)],
                'Time': [i/1000 for i in range(10)],
                'A': [(i*10)+10 for i in range(10)],
                'B': [(i*10)+20 for i in range(10)],
                }
        columns = ['Frame', 'Time', 'A', 'B']
        data_expected = pd.DataFrame(data, columns=columns)
        data_expected = data_expected.astype(dtype={'Frame': 'int', 'Time': 'float', 'A': 'float', 'B': 'float'})
        data_expected = data_expected.set_index('Frame')
        data_received = EmgData()
        data_path = self.get_data('data_two_tracks.emt')
        with open(data_path) as data_file:
            data_received.parse(data_file, columns[2:])
        pd.util.testing.assert_frame_equal(data_expected, data_received.data)


    def test_tracks(self):
        columns = ['Frame', 'Time', 'A', 'B']
        tracks = columns[2:]
        data_received = EmgData()
        data_path = self.get_data('data_two_tracks.emt')
        with open(data_path) as data_file:
            data_received.parse(data_file, tracks)
        self.assertListEqual(tracks, data_received.tracks)


    def test_frames(self):
        data = EmgData()
        data.data = pd.DataFrame([[0, 0, 1],
                                 [1, 1, 2],
                                 [2, 2, 3]],
                                 columns=['Frame', 'Time', 'A'])
        data.data = data.data.set_index(['Frame'])
        self.assertEqual(data.frames, 3)


    def test_max(self):
        data = EmgData()
        data.data = pd.DataFrame([[0, 0, 1],
                                 [1, 1, 2],
                                 [2, 2, 3]],
                                 columns=['Frame', 'Time', 'A'])
        data.data = data.data.set_index(['Frame'])
        self.assertEqual(data.max, 3)


    def test_min(self):
        data = EmgData()
        data.data = pd.DataFrame([[0, 0, 1],
                                 [1, 1, 2],
                                 [2, 2, 3]],
                                 columns=['Frame', 'Time', 'A'])
        data.data = data.data.set_index(['Frame'])
        self.assertEqual(data.min, 1)


    def test_split_data(self):
        data = EmgData()
        data.data = pd.DataFrame([[0, 0, 1],
                                 [1, 1, 2],
                                 [2, 2, 3]],
                                 columns=['Frame', 'Time', 'A'])
        data.data = data.data.set_index(['Frame'])
        time, data = data._split_data()

        expected_time = pd.DataFrame([[0, 0],
                                      [1, 1],
                                      [2, 2]],
                                      columns=['Frame', 'Time'])
        expected_time = expected_time.set_index(['Frame'])
        pd.util.testing.assert_frame_equal(time, expected_time)

        expected_data = pd.DataFrame([[0, 1],
                                      [1, 2],
                                      [2, 3]],
                                     columns=['Frame', 'A'])
        expected_data = expected_data.set_index(['Frame'])
        pd.util.testing.assert_frame_equal(data, expected_data)


    def test_new_data(self):
        df = pd.DataFrame([[0, 0, 1],
                           [1, 1, 2],
                           [2, 2, 3]],
                           columns=['Frame', 'Time', 'A'])
        df = df.set_index(['Frame'])
        data = EmgData._new_data(df)

        expected_data = EmgData()
        expected_data.data = pd.DataFrame([[0, 0, 1],
                                           [1, 1, 2],
                                           [2, 2, 3]],
                                          columns=['Frame', 'Time', 'A'])
        expected_data.data = expected_data.data.set_index(['Frame'])
        self.assertEqual(data, expected_data)


    def test_getitem(self):
        data = EmgData()
        data.data = pd.DataFrame([[0, 0, 1],
                                 [1, 1, 2],
                                 [2, 2, 3]],
                                 columns=['Frame', 'Time', 'A'])
        data.data = data.data.set_index(['Frame'])

        expected_data = pd.Series(data=[1, 2, 3],
                                  index=[0, 1, 2],
                                  name='A')
        expected_data.index.name = 'Frame'
        pd.util.testing.assert_series_equal(data['A'], expected_data)


    def test_eq(self):
        data_1 = EmgData()
        data_path = self.get_data('data_two_tracks.emt')
        tracks = ['A', 'B']
        with open(data_path) as data_file:
            data_1.parse(data_file, tracks=tracks)

        data_2 = EmgData()
        with open(data_path) as data_file:
            data_2.parse(data_file, tracks=tracks)
        self.assertTrue(data_1 == data_2)

        data_2 = EmgData()
        with open(data_path) as data_file:
            data_2.parse(data_file, tracks=['A', 'C'])
        self.assertFalse(data_1 == data_2)

        data_2 = EmgData()
        with open(data_path) as data_file:
            data_2.parse(data_file, tracks=tracks)
        data_2.data = data_1.data[['Time', 'A']]
        self.assertFalse(data_1 == data_2)

        data_2.data += 1
        self.assertFalse(data_1 == data_2)


    def test_norm_by_track(self):
        columns = ['Frame', 'Time', 'A', 'B']
        tracks = columns[2:]
        data_path = self.get_data('data_two_tracks_norm_by_track.emt')
        data_expected = pd.read_csv(data_path,
                                    sep='\t',
                                    names=columns,
                                    header=None,
                                    )
        data_expected = data_expected.astype(dtype={'Frame': 'int', 'Time': 'float', 'A': 'float', 'B': 'float'})
        data_expected = data_expected.set_index('Frame')

        data_path = self.get_data('data_two_tracks.emt')
        data_received = EmgData()
        with open(data_path) as data_file:
            data_received.parse(data_file, tracks)
        data_received = data_received.norm_by_track(tracks)
        pd.util.testing.assert_frame_equal(data_expected, data_received.data)


    def test_to_tsv(self):
        columns = ['Frame', 'Time', 'A', 'B']
        tracks = columns[2:]
        data_expected_path = self.get_data('data_two_tracks_norm_by_track.emt')
        data = EmgData()
        with open(data_expected_path) as data_file:
            data.parse(data_file, tracks)
        data_received = data.to_tsv(file=io.StringIO())

        with open(data_expected_path) as data_expected_file:
            for line_expected, line_recieved in zip(data_expected_file, data_received):
                self.assertEqual(line_expected, line_recieved)

        data_received = data.to_tsv()
        data_received = data_received.split('\n')
        with open(data_expected_path) as data_expected_file:
            for line_expected, line_recieved in zip(data_expected_file, data_received):
                self.assertEqual(line_expected, line_recieved + '\n')

    def test_group_track(self):
        data_1 = EmgData()
        data_1.data = pd.DataFrame([[0, 0, 1, 10],
                                    [1, 1, 2, 20],
                                    [2, 2, 3, 30]],
                                    columns=['Frame', 'Time', 'A', 'B'])
        data_1.data = data_1.data.set_index(['Frame'])

        data_2 = EmgData()
        data_2.data = pd.DataFrame([[0, 0, 1.2, 10.2],
                                    [1, 1, 2.2, 20.2],
                                    [2, 2, 3.2, 30.2]],
                                    columns=['Frame', 'Time', 'A', 'B'])
        data_2.data = data_2.data.set_index(['Frame'])

        expected_data = pd.DataFrame([[0, 0, 1, 1.2],
                                      [1, 1, 2, 2.2],
                                      [2, 2, 3, 3.2]],
                                    columns=['Frame', 'Time', 'exp_1', 'exp_2'])
        expected_data = expected_data.set_index(['Frame'])

        new_data = EmgData.group_track('A', {'exp_1': data_1, 'exp_2': data_2})
        pd.util.testing.assert_frame_equal(new_data.data, expected_data)

