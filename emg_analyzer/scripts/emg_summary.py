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
from emg_analyzer import emg
from emg_analyzer import argparse_utils
from emg_analyzer.utils import get_version_message



def main(args=None):
    """

    :param args:
    :return:
    """
    args = sys.argv[1:] if args is None else args

    parser = argparse.ArgumentParser()
    parser.add_argument('sum_path',
                        nargs='*',
                        default=sys.stdin,
                        help="The path to emg selection file '.sel' or a directory containing '.summary' files.")
    parser.add_argument('--version',
                        action=argparse_utils.VersionAction,
                        version=get_version_message(),
                        help='Display version and exit.')
    parser.add_argument('-o', '--output',
                        default=sys.stdout,
                        help='file to store results (default=stdout)'),
    parser.add_argument('-v', '--verbosity',
                        action='count',
                        default=0,
                        help="Set the output verbosity. can be set several times -vv for instance.")
    args = parser.parse_args(args)

    args.verbosity = max(10, 30 - (10 * args.verbosity))
    emg_analyzer.logger_set_level(args.verbosity)
    _log = colorlog.getLogger('emg_analyzer')

    if not isinstance(args.sum_path, list):
        # args must be read from stdin
        if sys.stdin.isatty():
            # stdin is empty
            msg = ''
            _log.error(msg)
            parser.print_help()
            sys.exit(msg)
        else:
            args.sum_path = [p.strip() for p in args.sum_path.readlines()]

    if not args.sum_path:
        parser.print_help()
        sys.exit(1)

    sum_file_to_aggregate = []
    for path in args.sum_path:
        path = path.strip()
        path = os.path.realpath(path)
        if os.path.isdir(path):
            for root, dirs, files in os.walk(path):
                sum_files = [os.path.join(root, f) for f in files if os.path.splitext(f)[1] == '.summary']
                sum_file_to_aggregate += sum_files
        elif os.path.isfile(path):
            sum_file_to_aggregate.append(path)

    summary = emg.desc_summary(sum_file_to_aggregate)
    summary = summary.round({'threshold': 4})

    if isinstance(args.output, str):
        dest_path = os.path.realpath(args.output) + '.summary'
        out = open(dest_path, 'w')
        to_close = True
    else:
        out = args.output
        to_close = False

    header = """# summary
# summary files= {emt}
# command line = {cmd_l}""".format(emt=' '.join(args.sum_path),
                                   cmd_l=" ".join(sys.argv))
    print(header, file=out)
    summary.to_csv(path_or_buf=out,
                   sep='\t',
                   na_rep='NaN')

    if to_close:
        out.close()


if __name__ == '__main__':
    main()
