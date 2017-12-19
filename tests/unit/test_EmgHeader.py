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
        self.assertListEqual(header.tracks_names, ['LDA~2'])

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
        self.assertListEqual(header.tracks_names, ['RDA~2', 'RTRI~2', 'RDP~2', 'RBI~2', 'RFLCar~2'])

        ################################################
        # header with tracks nb not match tracks names #
        ################################################
        header = EmgHeader()
        emt_path = self.get_data('header.bad_tracks_nb')
        with self.assertRaises(AssertionError) as ctx:
            with open(emt_path) as emt_file:
                header.parse(emt_file)
        self.assertEqual(str(ctx.exception),
                         "ERROR during parsing '{}': tracks number does not match tracks.".format(emt_path))

    def test_to_tsv(self):
        header = EmgHeader()
        emt_path = self.get_data('header.several_tracks')
        with open(emt_path) as emt_file:
            header.parse(emt_file)
        emt_file = StringIO()
        header.to_tsv(emt_file)
        generated_header = emt_file.getvalue()
        ori_header = open(emt_path).read()
        self.assertEqual(generated_header, ori_header)



