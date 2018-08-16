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

import pandas as pd

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
    parser.add_argument('dc_path',
                        help="The path to the directory containing '.emt' files to compute the min max for dinamyc calibration.")
    parser.add_argument('--output',
                        help="The name of the results files without extensions")
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

    if not os.path.isdir(args.dc_path):
        raise RuntimeError("The argument must be a directory: {}".format(parser.print_help()))

    dyn_cal = []
    emt_files = [p for p in os.listdir(args.dc_path) if os.path.isfile(os.path.join(args.dc_path, p))
                 and p.startswith('CD') and p.endswith('.emt')]
    _log.debug('emt files = {}'.format(emt_files))
    for emt in emt_files:
        filename, ext = os.path.splitext(emt)
        _log.info("Compute file " + str(filename))
        _, muscle, patient, *_ = filename.split('_')

        my_emg = emg.Emg()
        with open(os.path.join(args.dc_path, emt)) as f:
            my_emg.parse(f)

        data = my_emg.data.data
        _log.info("Extract col '{}' from file '{}'".format(muscle, emt))

        try:
            col = data[muscle]
        except KeyError:
            msg = "column '{}' not found in '{}".format(muscle, data.columns)
            _log.critical(msg)
            raise KeyError(msg) from None
        dyn_cal.append(col)
    if emt_files:
        dyn_cal = pd.concat(dyn_cal, axis=1)
    else:
        _log.warning("No columns found")
        sys.exit(0)
    if args.output is None:
        args.output = os.path.join(args.dc_path, "{}_dyn_cal".format(patient))

    dest_file = args.output + '.emt'
    with open(dest_file, 'w') as f:
        print('#EMG for Dynamic Calibration', file=f)
        print('# {}'.format(' '.join(sys.argv)), file=f)
        dyn_cal.to_csv(path_or_buf=f,
                       sep='\t',
                       float_format='%.3f',
                       na_rep='NaN')

    dest_file = args.output + '.desc'
    desc = dyn_cal.describe()
    with open(dest_file, 'w') as f:
        print('#value for Dynamic Calibration', file=f)
        print('# {}'.format(' '.join(sys.argv)), file=f)
        desc.to_csv(path_or_buf=f,
                    sep='\t',
                    float_format='%.3f',
                    na_rep='NaN')
