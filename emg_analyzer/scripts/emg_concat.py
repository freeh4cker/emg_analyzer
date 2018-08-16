#! /usr/bin/env python3
# -*- coding: utf-8 -*-

##########################################################################
# Copyright (c) 2017-2018 Bertrand Néron. All rights reserved.           #
# Use of this source code is governed by a BSD-style license that can be #
# found in the LICENSE file.                                             #
##########################################################################

import argparse
import os
import sys
import colorlog
import emg_analyzer
from emg_analyzer import argparse_utils
from emg_analyzer.utils import  get_version_message



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

    emt_to_concat = []
    for path in args.emg_path:
        path = path.strip()
        path = os.path.realpath(path)
        if os.path.isdir(path):
            for root, dirs, files in os.walk(path):
                emt_files = [f for f in files if os.path.splitext(f)[1] == '.emt']
                emt_to_concat += emt_files
        elif os.path.isfile(path):
            emt_to_concat.append(path)

    emg_to_concat = []
    for emt in emt_to_concat:
        with open(emt) as f:
            emg = emg_analyzer.emg.Emg()
            emg.parse(f)
            emg_to_concat.append(emg)

    concat = emg_analyzer.emg.EMGConcat(*emg_to_concat)
    concat_name = '_'.join(concat.emg_names)
    with open(concat_name + '.concat', 'w') as f:
        concat.to_tsv(file=f)

    df = concat.describe()
    with open(concat_name + '.describe') as f:
        df.to_csv(path_or_buf=f,
                  sep='\t',
                  float_format='%.3f',
                  na_rep='NaN')
    print(df)


if __name__ == '__main__':
    main()
