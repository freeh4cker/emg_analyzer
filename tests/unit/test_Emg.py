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


    def test_norm_by_track(self):
        emg = Emg()
        emt_path = self.get_data('two_tracks.emt')
        with open(emt_path) as emt_file:
            emg.parse(emt_file)
        emg.norm_by_track()

        emt_norm_path = self.get_data('two_tracks_norm.emt')
        norm_emg = Emg()
        with open(emt_norm_path) as emt_norm_file:
            norm_emg.parse(emt_norm_file)
        self.assertEqual(emg, norm_emg)

    def test_to_emt(self):
        emg = Emg()
        emt_path = self.get_data('two_tracks_norm.emt')
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
            for line_expected, line_recieved in zip(emg_expected, emg_received):
                self.assertEqual(line_expected, line_recieved + '\n')