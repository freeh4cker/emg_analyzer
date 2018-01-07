##########################################################################
# Copyright (c) 2017-2018 Bertrand Néron. All rights reserved.                #
# Use of this source code is governed by a BSD-style license that can be #
# found in the LICENSE file.                                             #
##########################################################################

import tempfile
import shutil
import os

try:
    from tests import EmgTest
except ImportError as err:
    msg = "Cannot import emg_analyzer: {0!s}".format(err)
    raise ImportError(msg)

from emg_analyzer import utils

import logging

# get the logger quiet
emg_logger = logging.getLogger('emg_analyzer')
stream_handler = emg_logger.handlers[0]
emg_logger.removeHandler(stream_handler)
emg_logger.addHandler(logging.NullHandler())


class TestUtils(EmgTest):

    def process_one_emt_file(self):
        emt_path_ori = self.get_data('two_tracks.emt')
        emt_path_exp = self.get_data('two_tracks_norm_by_track.emt')
        with tempfile.TemporaryDirectory() as tmp_dir_name:
            emt_path = shutil.copy(emt_path_ori, tmp_dir_name)
            norm_path = utils.process_one_emt_file(emt_path,
                                                   'norm_by_track',
                                                   method_args=tuple(),
                                                   method_kwargs={},
                                                   dest=tmp_dir_name,
                                                   suffix='norm')
            self.assertTrue(self.compare_2_files(norm_path, emt_path_exp))


    def test_process_dir(self):
        emt_path_ori = self.get_data('two_tracks.emt')
        emt_path_exp = self.get_data('two_tracks_norm_by_track.emt')
        with tempfile.TemporaryDirectory() as tmp_dir_name:

            # create 3 nested directories with one emt file in each
            level = tmp_dir_name
            for i in (0, 1, 2):
                level = os.path.join(level, 'level{}'.format(i))
                os.mkdir(level)
                shutil.copy(emt_path_ori, level)

            norm_path = utils.process_dir(os.path.join(tmp_dir_name, 'level0'),
                                          'norm_by_track',
                                          method_args=tuple(),
                                          method_kwargs={},
                                          suffix='norm'
                                          )

            level = tmp_dir_name
            for i in (0, 1, 2):
                level = os.path.join(level, 'level{}'.format(i))
                self.assertTrue(os.path.exists(norm_path))
                self.assertTrue(os.path.isdir(norm_path))
                self.assertTrue(self.compare_2_files(os.path.join(norm_path, 'two_tracks_norm.emt'),
                                                     emt_path_exp))

            with self.assertRaises(IOError) as ctx:
                utils.process_dir(os.path.join(tmp_dir_name, 'level0'),
                                  'norm_by_track',
                                  method_args=tuple(),
                                  method_kwargs={},
                                  suffix='norm'
                                  )
                self.assertEqual(str(ctx.exception),
                                'directory exists: {}'.format(os.path.join(tmp_dir_name, 'level0_norm')))
