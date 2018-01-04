#! /usr/bin/env python3
# -*- coding: utf-8 -*-

##########################################################################
# Copyright (c) 2017 Bertrand Néron. All rights reserved.                #
# Use of this source code is governed by a BSD-style license that can be #
# found in the LICENSE file.                                             #
##########################################################################

import argparse
import os
import sys
from emg_analyzer import emg
from emg_analyzer import argparse_utils


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


def norm_one_emg_file(emg_path, dest=''):
    """
    Normalize an EMG ('.emt') file.
    Create a new file postpend with '_norm'.

    :param str emg_path: the path of the emt file to normalize
    :param str dest: the directory to put the normalized file,
                     default is current working directory
    :return: the path of the normalized file.
    :rtype: str
    """
    my_emg = emg.Emg()
    with open(emg_path) as emg_file:
        my_emg.parse(emg_file)
    my_emg.norm()

    root_dir, basename = os.path.split(emg_path)
    normed_filename, ext = os.path.splitext(basename)
    normed_filename = normed_filename.replace(' ', '_')
    normed_filename = "{}_norm{}".format(normed_filename, ext)
    normed_path = os.path.join(dest, normed_filename)

    with open(normed_path, 'w') as normed_file:
        my_emg.to_emt(file=normed_file)
    return normed_path

def norm_one_dir(path, dest=''):
    """
    walk recursively through path and norm each .emt file
    a new tree file postpend with '_norm' is created.

    :param str path: the path of the emt file/dir to normalize
    :param str dest: the directory to put the normalized file
    :return: the path of the normalized directory.
    :rtype: str
    """
    path = path.rstrip(os.sep)
    root_dir, basename = os.path.split(path)
    norm_dir = "{}_norm".format(basename.replace(' ', '_'))
    if dest:
        norm_path = os.path.join(dest, norm_dir)
    else:
        norm_path = os.path.join(root_dir, norm_dir)
    os.mkdir(norm_path)
    with os.scandir(path) as dir_it:
        for entry in dir_it:
            if not entry.name.startswith('.') and entry.is_file() and entry.name.endswith('.emt'):
                print("Normalizing", entry.path, file=sys.stderr)
                norm_one_emg_file(entry.path, dest=norm_path)
            elif entry.is_dir():
                norm_one_dir(entry.path, dest=norm_path)
    return norm_path


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
            norm_one_dir(path)
        else:
            norm_one_emg_file(path)


if __name__ == '__main__':
    main()
