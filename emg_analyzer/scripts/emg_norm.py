#! /usr/bin/env python3
# -*- coding: utf-8 -*-

##########################################################################
# Copyright (c) 2017-2018 Bertrand Néron. All rights reserved.                #
# Use of this source code is governed by a BSD-style license that can be #
# found in the LICENSE file.                                             #
##########################################################################

import argparse
import os
import sys
from emg_analyzer import argparse_utils
from emg_analyzer.utils import process_dir, process_one_emt_file


def get_version_message():
    import emg_analyzer
    import pandas
    import numpy
    version_text = """emg_norm: {emg_vers}

Using: 
    - pandas: {pd_vers}
    - numpy: {np_vers}""".format(emg_vers=emg_analyzer.__version__,
                                 pd_vers=pandas.__version__,
                                 np_vers=numpy.__version__)
    return version_text


def main(args=None):
    """

    :param args:
    :return:
    """
    args = sys.argv[1:] if args is None else args

    parser = argparse.ArgumentParser()
    parser.add_argument('emg_path',
                        nargs='+',
                        help="The path to '.emt' file or a directory containing '.emt' files.")
    parser.add_argument('--version',
                        action=argparse_utils.VersionAction,
                        version=get_version_message(),
                        help='Display version and exit.')

    args = parser.parse_args(args)
    for path in args.emg_path:
        if os.path.isdir(path):
            process_dir(path,
                        'norm',
                        method_args=tuple(),
                        method_kwargs={},
                        suffix='norm'
                        )
        else:
            process_one_emt_file(path,
                                 'norm',
                                 method_args=tuple(),
                                 method_kwargs={},
                                 suffix='norm'
                                 )


if __name__ == '__main__':
    main()
