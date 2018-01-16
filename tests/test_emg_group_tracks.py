##########################################################################
# Copyright (c) 2017-2018 Bertrand Néron. All rights reserved.                #
# Use of this source code is governed by a BSD-style license that can be #
# found in the LICENSE file.                                             #
##########################################################################


import tempfile
import os
import sys

try:
    from tests import EmgTest
except ImportError as err:
    msg = "Cannot import emg_analyzer: {0!s}".format(err)
    raise ImportError(msg)

from emg_analyzer.scripts import emg_group_tracks


class Test_emg_group_track(EmgTest):


    def test_main_version(self):
        import sys
        real_exit = sys.exit

        def fake_exit(*args, **kwargs):
            raise TypeError()

        sys.exit = fake_exit
        with self.catch_output(out=True) as flow:
            try:
                emg_group_tracks.main(args=['--version'])
            except TypeError:
                out, err = flow
                import emg_analyzer
                expected_msg = """emg_group_tracks: {emg_vers}

Using: 
    - pandas: {pd_vers}
    - numpy: {np_vers}
    - python: {py_vers}
""".format(emg_vers=emg_analyzer.__version__,
                                  pd_vers=emg_analyzer.emg.pd.__version__,
                                  np_vers=emg_analyzer.emg.np.__version__,
                                  py_vers='.'.join([str(i) for i in sys.version_info[0:3]])
                                  )
            finally:
                sys.exit = real_exit
        msg = out.getvalue()
        self.assertEqual(msg, expected_msg)


    def test_out_dir(self):
        input_emg = [self.get_data('exp{}.emt'.format(i)) for i in (1, 2, 3, 4)]
        with tempfile.TemporaryDirectory() as tmp_dir_name:
            out_dir = os.path.join(tmp_dir_name, 'foo')
            emg_group_tracks.main(args=['--out-dir', out_dir, *input_emg])
            self.assertTrue(os.path.exists(out_dir))
            self.assertTrue(os.path.isdir(out_dir))

        with tempfile.TemporaryDirectory() as tmp_dir_name:
            out_dir = os.path.join(tmp_dir_name, 'foo')
            open(out_dir, 'w').close()
            with self.assertRaises(IOError) as ctx:
                emg_group_tracks.main(args=['--out-dir', out_dir, *input_emg])
            self.assertEqual(str(ctx.exception),
                             "'{}' is not a directory".format(out_dir)
                             )

        with tempfile.TemporaryDirectory() as tmp_dir_name:
            out_dir = os.path.join(tmp_dir_name, 'foo')
            os.mkdir(out_dir, 111)
            with self.assertRaises(IOError) as ctx:
                emg_group_tracks.main(args=['--out-dir', out_dir, *input_emg])
            self.assertEqual(str(ctx.exception),
                             "'{}' is not writable".format(out_dir)
                             )
            os.chmod(out_dir, 777)

        cwd = os.getcwd()
        exp_emg = {i: self.get_data('{}.emt'.format(i)) for i in ('A', 'B', 'C')}
        with tempfile.TemporaryDirectory() as tmp_dir_name:
            os.chdir(tmp_dir_name)
            emg_group_tracks.main(args=[ *input_emg])
            for f in exp_emg:
                self.assertTrue(self.compare_2_files(exp_emg[f],
                                                     os.path.join(tmp_dir_name, f + '.emt')
                                                     )
                                )
        os.chdir(cwd)


    def test_main(self):
        input_emg = [self.get_data('exp{}.emt'.format(i)) for i in (1, 2, 3, 4)]
        exp_emg = {i: self.get_data('{}.emt'.format(i)) for i in ('A', 'B', 'C')}
        with tempfile.TemporaryDirectory() as tmp_dir_name:
            emg_group_tracks.main(args=['--out-dir', tmp_dir_name, *input_emg])
            for f in exp_emg:
                self.assertTrue(self.compare_2_files(exp_emg[f],
                                                     os.path.join(tmp_dir_name, f + '.emt')
                                                     )
                                )

        with tempfile.TemporaryDirectory() as tmp_dir_name:
            file = os.path.join(tmp_dir_name, 'A.emt')
            open(file, 'w').close()
            with self.assertRaises(IOError) as ctx:
                emg_group_tracks.main(args=['--out-dir', tmp_dir_name, *input_emg])
            self.assertEqual(str(ctx.exception),
                             'file already exists: {}'.format(file)
                             )