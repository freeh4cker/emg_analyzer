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
            args.print_help()
            sys.exit(msg)
        else:
            args.emg_path = [p.strip() for p in args.emg_path.readlines()]

    if not args.emg_path:
        args.print_help()
        sys.exit(1)

    norm_method = 'norm_by_track' if args.by_track else 'norm'
    _log.debug("morm_method = '{}'".format(norm_method))

    for path in args.emg_path:
        path = path.strip()
        if os.path.isdir(path):
            processed = process_dir(path,
                                    norm_method,
                                    method_args=tuple(),
                                    method_kwargs={},
                                    suffix='norm'
                                    )
        else:
            processed = process_one_emt_file(path,
                                             norm_method,
                                             method_args=tuple(),
                                             method_kwargs={},
                                             suffix='norm'
                                             )
        print(processed)


if __name__ == '__main__':
    main()
