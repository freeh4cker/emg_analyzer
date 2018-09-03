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

from emg_analyzer.emg import EmgHeader


class TestEmgHeader(EmgTest):

    def test_parse(self):
        header = EmgHeader()
        emt_path = self.get_data('header.unix')
        with open(emt_path) as emt_file:
            header.parse(emt_file)
        self.assertEqual(header.type, 'Emg tracks')
        self.assertEqual(header.unit, 'V')
        self.assertEqual(header.tracks_nb, 1)
        self.assertEqual(header.freq, '1000 Hz')
        self.assertEqual(header.frames, 33780)
        self.assertEqual(header.start_time, 0.000)
        self.assertListEqual(header.tracks_names, ['LDA'])

        ##################################
        # header with frame not indented #
        ##################################
        header = EmgHeader()
        emt_path = self.get_data('header.bad_frame')
        with self.assertRaises(AssertionError) as ctx:
            with open(emt_path) as emt_file:
                header.parse(emt_file)
        self.assertEqual(str(ctx.exception),
                         "ERROR during parsing '{}': tracks_names".format(emt_path))

        ##############################
        # header with several tracks #
        ##############################
        header = EmgHeader()
        emt_path = self.get_data('header.several_tracks')
        with open(emt_path) as emt_file:
            header.parse(emt_file)
        self.assertEqual(header.type, 'Emg tracks')
        self.assertEqual(header.unit, 'V')
        self.assertEqual(header.tracks_nb, 5)
        self.assertEqual(header.freq, '1000 Hz')
        self.assertEqual(header.frames, 20850)
        self.assertEqual(header.start_time, 0.000)
        self.assertListEqual(header.tracks_names, ['RDA', 'RTRI', 'RDP', 'RBI', 'RFLCar'])

        ################################################
        # header with tracks nb not match tracks names #
        ################################################
        header = EmgHeader()
        emt_path = self.get_data('header.bad_tracks_nb')
        with self.assertRaises(AssertionError) as ctx:
            with open(emt_path) as emt_file:
                header.parse(emt_file)
        self.assertEqual(str(ctx.exception),
                         "ERROR during parsing '{}': tracks number '2' does not match tracks: "
                         "RDA, RTRI, RDP, RBI, RFLCar.".format(emt_path))

    def test_eq(self):
        header_1 = EmgHeader()
        header_path = self.get_data('header_two_tracks.emt')
        with open(header_path) as header_file:
            header_1.parse(header_file)

        header_2 = EmgHeader()
        with open(header_path) as header_file:
            header_2.parse(header_file)
        self.assertTrue(header_1 == header_2)

        header_2.tracks_nb += 1
        self.assertFalse(header_1 == header_2)


    def test_copy(self):
        header_1 = EmgHeader()
        header_path = self.get_data('header_two_tracks.emt')
        with open(header_path) as header_file:
            header_1.parse(header_file)

        header_2 = header_1.copy()
        self.assertFalse(header_1 is header_2)
        self.assertEqual(header_1, header_2)


    def test_to_tsv(self):
        header = EmgHeader()
        emt_path = self.get_data('header.several_tracks')
        with open(emt_path) as emt_file:
            header.parse(emt_file)
        emt_file = StringIO()
        header.to_tsv(file=emt_file)
        generated_header = emt_file.getvalue()
        with open(emt_path) as ref_file:
            ori_header = ref_file.read()
        self.assertEqual(generated_header, ori_header)

        header_received = header.to_tsv()
        header_received = header_received.split('\n')
        with open(emt_path) as header_expected:
            for line_expected, line_recieved in zip(header_expected, header_received):
                self.assertEqual(line_expected, line_recieved + '\n')


