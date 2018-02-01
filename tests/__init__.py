##########################################################################
# Copyright (c) 2017-2018 Bertrand Néron. All rights reserved.                #
# Use of this source code is governed by a BSD-style license that can be #
# found in the LICENSE file.                                             #
##########################################################################


import os
import unittest
import sys
from io import StringIO
from contextlib import contextmanager

class EmgTest(unittest.TestCase):

    _data_dir = os.path.normpath(os.path.join(os.path.dirname(__file__), "data"))

    def get_data(self, path):
        data_path = os.path.join(self._data_dir, path)
        if not os.path.exists(data_path):
            raise FileNotFoundError("{} not found".format(data_path))
        return data_path

    def compare_2_files(self, f1, f2):
        with open(f1) as fh1, open(f2) as fh2:
            return fh1.read() == fh2.read()

    @contextmanager
    def catch_output(self, out=False, err=False):
        """
        Catch stderr and stdout of the code running within this block.
        """
        old_out = sys.stdout
        new_out = old_out
        old_err = sys.stderr
        new_err = old_err
        if out:
            new_out = StringIO()
        if err:
            new_err = StringIO()
        try:
            sys.stdout, sys.stderr = new_out, new_err
            yield sys.stdout, sys.stderr
        finally:
            sys.stdout, sys.stderr = old_out, old_err
