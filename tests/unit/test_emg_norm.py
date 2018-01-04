import tempfile
import shutil
import os

try:
    from tests import EmgTest
except ImportError as err:
    msg = "Cannot import emg_analyzer: {0!s}".format(err)
    raise ImportError(msg)

from emg_analyzer.scripts import emg_norm


class TestEmgData(EmgTest):

    def test_get_version_message(self):
        import emg_analyzer
        import pandas
        import numpy
        expected_msg = """emg_norm: {emg_vers}

Using: 
    - pandas: {pd_vers}
    - numpy: {np_vers}""".format(emg_vers=emg_analyzer.__version__,
                                 pd_vers=pandas.__version__,
                                 np_vers=numpy.__version__)
        self.assertEqual(emg_norm.get_version_message(), expected_msg)


    def test_norm_one_emg_file(self):
        emt_path_ori = self.get_data('two_tracks.emt')
        emt_path_exp = self.get_data('two_tracks_norm.emt')
        with tempfile.TemporaryDirectory() as tmp_dir_name:
            emt_path = shutil.copy(emt_path_ori, tmp_dir_name)
            norm_path = emg_norm.norm_one_emg_file(emt_path, dest=tmp_dir_name)
            self.assertTrue(self.compare_2_files(norm_path, emt_path_exp))


    def test_norm_one_dir(self):
        emt_path_ori = self.get_data('two_tracks.emt')
        emt_path_exp = self.get_data('two_tracks_norm.emt')
        with self.catch_output(err=True):
            with tempfile.TemporaryDirectory() as tmp_dir_name:

                # create 3 nested directories with one emt file in each
                level = tmp_dir_name
                for i in (0, 1, 2):
                    level = os.path.join(level, 'level{}'.format(i))
                    os.mkdir(level)
                    shutil.copy(emt_path_ori, level)

                norm_path = emg_norm.norm_one_dir(os.path.join(tmp_dir_name, 'level0'))

                level = tmp_dir_name
                for i in (0, 1, 2):
                    level = os.path.join(level, 'level{}'.format(i))
                    self.assertTrue(os.path.exists(norm_path))
                    self.assertTrue(os.path.isdir(norm_path))
                    self.assertTrue(self.compare_2_files(os.path.join(norm_path, 'two_tracks_norm.emt'),
                                                         emt_path_exp))

    def compare_2_files(self, f1, f2):
        return open(f1).read() == open(f2).read()
