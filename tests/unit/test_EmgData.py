import pandas as pd

try:
    from tests import EmgTest
except ImportError as err:
    msg = "Cannot import emg_analyzer: {0!s}".format(err)
    raise ImportError(msg)

from emg_analyzer.emg import EmgData


class TestEmgData(EmgTest):

    def test_parse(self):
        columns = ['Frame', 'Time', 'A']
        data_expected = pd.DataFrame([[i, i/1000, (i*10)+10] for i in range(10)], columns=columns)
        data_expected = data_expected.astype(dtype={'Frame': 'int', 'Time': 'float', 'A': 'float'})
        data_expected = data_expected.set_index('Frame')
        data_recieved = EmgData()
        data_path = self.get_data('data_one_track.emt')
        with open(data_path) as data_file:
            data_recieved.parse(data_file, columns[2:])
        pd.util.testing.assert_frame_equal(data_expected, data_recieved.data)

    def test_muscles(self):
        pass

    def test_norm_tracks(self):
        pass

    def test_to_tsv(self):
        pass