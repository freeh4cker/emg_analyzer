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
from numpy import nan
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
    parser.add_argument('--rest-matrix',
                       required=True,
                       help="the file describing (with statistics) the rest condition")
    parser.add_argument('--coef',
                        type=float,
                        default=1.5,
                        help='the multiplying coeficient to apply to the standard deviation')
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

    emt_to_filter = []
    for path in args.emg_path:
        path = path.strip()
        path = os.path.realpath(path)
        if os.path.isdir(path):
            for root, dirs, files in os.walk(path):
                emt_files = [os.path.join(root, f) for f in files if os.path.splitext(f)[1] == '.emt']
                emt_to_filter += emt_files
        elif os.path.isfile(path):
            emt_to_filter.append(path)

    emg_to_filter = []
    for emt in emt_to_filter:
        with open(emt) as f:
            emg = emg_analyzer.emg.Emg()
            emg.parse(f)
            emg_to_filter.append(emg)

    rest_matrix =pd.read_table(args.rest_matrix, comment='#', index_col=0)
    for emg, path in zip(emg_to_filter, emt_to_filter):
        _log.info('Compute emg ' + path)
        sel, thresholds = emg.select(rest_matrix, coef=args.coef)
        data = sel.data.data
        data.index.name = 'Frame'

        dest_path = os.path.splitext(path)[0] + '.sel'
        _log.info('Write file ' + dest_path)
        with open(dest_path, 'w') as f:
            print('# Activities selection', file=f)
            print("# filter {} emg with rest matrix = {}".format(' '.join(args.emg_path), args.rest_matrix), file=f)
            print("# {}".format(" ".join(sys.argv)), file=f)
            data.to_csv(path_or_buf=f,
                        sep='\t',
                        float_format='%.3f',
                        na_rep='NaN')

        thresholds = pd.Series(thresholds, dtype=float)
        thresholds = thresholds.round(decimals=4)
        count = pd.Series(data.describe().loc['count'], dtype=int)
        count.sort_index(inplace=True)
        frames_num = len(sel.data.data)
        activation_ratio = count / frames_num
        activation_ratio = activation_ratio.round(decimals=2)
        summary = pd.concat([thresholds, count, activation_ratio], axis=1,
                            sort=True)
        summary.columns = ['threshold', 'count', 'activation_ratio']
        summary.index.name = 'muscle'
        summary = summary[1:]

        dest_path = os.path.splitext(path)[0] + '_sel.summary'
        _log.info('Write file ' + dest_path)
        with open(dest_path, 'w') as f:
            print("# Summary of activities for condition: {}".format(os.path.basename(path)), file=f)
            summary.to_csv(path_or_buf=f,
                           sep='\t',
                           na_rep='NaN')


if __name__ == '__main__':
    main()
