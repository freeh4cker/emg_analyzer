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
import colorlog
import emg_analyzer
from emg_analyzer import argparse_utils
from emg_analyzer.utils import get_version_message


def main(args=None):
    """

    :param args:
    :return:
    """
    args = sys.argv[1:] if args is None else args
    desc = """
emg_group_tracks take several emt files as input and groups tracks base on their names.
Creates one .emt file by tracks. for instance:

inputs:
-------
exp1.emt
    track_A track_B track_C track_D

exp2.emt
    track_B track_A track_D track_D

exp3.emt
    track_D track_C track_D track_C

outputs:
--------
track_A.emt
    exp1 exp2 exp3

track_B.emt
    exp1 exp2 exp3

track_C.emt
    exp1 exp2 exp3

track_D.emt
    exp1 exp2 exp3

"""
    parser = argparse.ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter,
                                     description=desc)
    parser.add_argument('emg_path',
                        nargs='*',
                        default=sys.stdin,
                        help="The path to '.emt' files to group by tracks.")
    parser.add_argument('--out-dir',
                        help='directory where to write results, if directory does not exists, it will be created')
    parser.add_argument('--version',
                        action=argparse_utils.VersionAction,
                        version=get_version_message(),
                        help='Display version and exit.')
    parser.add_argument('-v', '--verbosity',
                        action='count',
                        default=0,
                        help="Set the output verbosity. can be set several times -vv for instance.")
    args = parser.parse_args(args)

    args.verbosity = max(10, 30 - (10 * args.verbosity))
    emg_analyzer.logger_set_level(args.verbosity)
    _log = colorlog.getLogger('emg_analyzer')

    if args.out_dir:
        args.out_dir = os.path.realpath(args.out_dir)
        _log.debug("out_dir = " + args.out_dir)

        if not os.path.exists(args.out_dir):
            os.mkdir(args.out_dir)
        elif not os.path.isdir(args.out_dir):
            msg = "'{}' is not a directory".format(args.out_dir)
            _log.error(msg)
            raise IOError(msg)
        elif not os.access(args.out_dir, os.W_OK):
            msg = "'{}' is not writable".format(args.out_dir)
            _log.error(msg)
            raise IOError(msg)
    else:
        args.out_dir = ''

    input_emg = []

    for path in args.emg_path:
        emg = emg_analyzer.emg.Emg()
        with open(path) as f:
            _log.info("Parsing {}".format(path))
            emg.parse(f)
        input_emg.append(emg)

    new_emg = input_emg[0].group_by_track(input_emg[1:])

    for emg in new_emg:
        emg_path = os.path.join(args.out_dir, emg.name + '.emt')
        results = []
        if os.path.exists(emg_path):
            msg = 'file already exists: {}'.format(emg_path)
            _log.error(msg)
            raise IOError(msg)
        with open(emg_path, 'w') as f:
            _log.info("Writing {}".format(emg_path))
            emg.to_emt(f)
            results.append(emg_path)
    if args.out_dir:
        print(args.out_dir)
    else:
        print(' '.join(results))


if __name__ == '__main__':
    main()
