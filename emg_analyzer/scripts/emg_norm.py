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

import pandas as pd

import emg_analyzer
from emg_analyzer import argparse_utils
from emg_analyzer.utils import process_dir, process_one_emt_file, get_version_message



def main(args=None):
    """

    :param args:
    :return:
    """
    args = sys.argv[1:] if args is None else args

    parser = argparse.ArgumentParser()
    parser.add_argument('emg_path',
                        nargs='*',
                        default=sys.stdin,
                        help="The path to '.emt' file or a directory containing '.emt' files.")
    parser.add_argument('--by-track',
                        action='store_true',
                        default=False,
                        help='normalize track by track instead of all tracks together')
    parser.add_argument('--min',
                        type=float,
                        help='the min value to use for the normalization '
                             '(default use the min value of the matrix or column)')
    parser.add_argument('--max',
                        type=float,
                        help='the max value to use for the normalization '
                             '(default use the max value of the matrix or column)')
    parser.add_argument('--dyn-cal',
                        help='The path to the file to use for the dynamic calibration.')
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

    if not isinstance(args.emg_path, list):
        # args must be read from stdin
        if sys.stdin.isatty():
            # stdin is empty
            msg = ''
            _log.error(msg)
            parser.print_help()
            sys.exit(msg)
        else:
            args.emg_path = [p.strip() for p in args.emg_path.readlines()]

    if not args.emg_path:
        parser.print_help()
        sys.exit(1)

    norm_method = 'norm_by_track' if args.by_track or args.dyn_cal else 'norm'

    _log.debug("morm_method = '{}'".format(norm_method))
    options = {}
    if args.min is not None:
        options['min'] = args.min
    if args.max is not None:
        options['max'] = args.max
    if args.dyn_cal:
        _log.info("Loading dynamic calibration file '{}'".format(args.dyn_cal))
        dyn_cal = pd.read_table(args.dyn_cal, comment='#', index_col=0)
        dyn_cal = dyn_cal.T[['min', 'max']].T
        print(dyn_cal)
        options['dyn_cal'] = dyn_cal

    for path in args.emg_path:
        path = path.strip()
        if os.path.isdir(path):
            processed = process_dir(path,
                                    norm_method,
                                    method_args=tuple(),
                                    method_kwargs=options,
                                    suffix='norm'
                                    )
        else:
            processed = process_one_emt_file(path,
                                             norm_method,
                                             method_args=tuple(),
                                             method_kwargs=options,
                                             suffix='norm'
                                             )
        print(processed)


if __name__ == '__main__':
    main()
