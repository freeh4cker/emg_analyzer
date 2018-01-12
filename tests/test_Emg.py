##########################################################################
# Copyright (c) 2017-2018 Bertrand Néron. All rights reserved.                #
# Use of this source code is governed by a BSD-style license that can be #
# found in the LICENSE file.                                             #
##########################################################################


from io import StringIO

try:
    from tests import EmgTest
except ImportError as err:
    msg = "Cannot import emg_analyzer: {0!s}".format(err)
    raise ImportError(msg)

from emg_analyzer.emg import Emg, EmgHeader, EmgData


class TestEmg(EmgTest):

    def test_parse(self):
        emt_path = self.get_data('two_tracks.emt')
        emg = Emg()
        with open(emt_path) as emt_file:
            emg.parse(emt_file)

        expected_header = EmgHeader()
        header_path = self.get_data('header_two_tracks.emt')
        with open(header_path) as header_file:
            expected_header.parse(header_file)
        self.assertEqual(emg.header, expected_header)

        expected_data = EmgData()
        data_path = self.get_data('data_two_tracks.emt')
        with open(data_path) as data_file:
            expected_data.parse(data_file, tracks=expected_header.tracks_names)
        self.assertEqual(emg.data, expected_data)
        self.assertEqual(emg.name, 'two_tracks')


    def test_norm(self):
        emg = Emg()
        emt_path = self.get_data('two_tracks.emt')
        with open(emt_path) as emt_file:
            emg.parse(emt_file)
        norm_emg = emg.norm()

        expected_emt_path = self.get_data('two_tracks_norm.emt')
        expected_emg = Emg()
        with open(expected_emt_path) as expected_emt_file:
            expected_emg.parse(expected_emt_file)
        self.assertEqual(expected_emg, norm_emg)


    def test_norm_by_track(self):
        emg = Emg()
        emt_path = self.get_data('two_tracks.emt')
        with open(emt_path) as emt_file:
            emg.parse(emt_file)
        norm_emg = emg.norm_by_track()

        expected_emt_path = self.get_data('two_tracks_norm_by_track.emt')
        expected_emg = Emg()
        with open(expected_emt_path) as expected_emt_file:
            expected_emg.parse(expected_emt_file)
        self.assertEqual(expected_emg, norm_emg)


    def test_to_emt(self):
        emg = Emg()
        emt_path = self.get_data('two_tracks_norm_by_track.emt')
        with open(emt_path) as emt_file:
            emg.parse(emt_file)
        emt_file = StringIO()
        emg.to_emt(file=emt_file)
        generated_emt = emt_file.getvalue()
        ori_emt = open(emt_path).read()
        self.assertEqual(generated_emt, ori_emt)

        emg_received = emg.to_emt()
        emg_received = emg_received.split('\n')
        with open(emt_path) as emg_expected:
            for line_expected, line_received in zip(emg_expected, emg_received):
                self.assertEqual(line_expected, line_received + '\n')


    def test_group_by_track(self):
        e1, e2, e3,  e4 = Emg(), Emg(), Emg(), Emg()

        with open(self.get_data('exp1.emt')) as f:
            e1.parse(f)
        with open(self.get_data('exp2.emt')) as f:
            e2.parse(f)
        with open(self.get_data('exp3.emt')) as f:
            e3.parse(f)
        with open(self.get_data('exp4.emt')) as f:
            e4.parse(f)

        new_d = e1.group_by_track([e2, e3, e4])
        self.assertEqual(len(new_d), 3)

        A, B, C = Emg(), Emg(), Emg()

        with open(self.get_data('A.emt')) as f:
            A.parse(f)
        with open(self.get_data('B.emt')) as f:
            B.parse(f)
        with open(self.get_data('C.emt')) as f:
            C.parse(f)

        for emg_expected in (A, B, C):
            self.assertIn(emg_expected, new_d)

        more_frames = Emg()
        with open(self.get_data('exp2_more_frames.emt')) as f:
            more_frames.parse(f)

        #with self.assertRaises(RuntimeError) as ctx:
        #    new_d = e1.group_by_track([more_frames])