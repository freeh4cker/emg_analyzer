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

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

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

"""
    parser = argparse.ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter,
                                     description=desc)
    parser.add_argument('sum_path',
                        nargs='*',
                        default=sys.stdin,
                        help="The path to '.summary' files to merge.")
    parser.add_argument('--out-dir',
                        help='directory where to write results, if directory does not exists, it will be created')
    parser.add_argument('--version',
                        action=argparse_utils.VersionAction,
                        version=get_version_message(),
                        help='Display version and exit.')
    parser.add_argument('--active',
                        required=True,
                        nargs='+',
                        help='the list of active muscles (separate by space)'
                        )
    parser.add_argument('--inactive',
                        required=True,
                        nargs='+',
                        help='the list of inactive muscles (separate by space)'
                        )
    parser.add_argument('--mvt',
                        required=True,
                        help='movement type')
    parser.add_argument('--patient',
                        required=True,
                        help='name of the patient')
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

    summaries = [pd.read_table( path, comment="#", index_col=0) for path in args.sum_path]
    act_ratio = [df.activation_ratio for df in summaries]
    ratio = pd.concat(act_ratio, axis=1)
    ratio.columns = list(range(1, len(args.sum_path) + 1))
    desc = ratio.T.describe()

    dest_path = "{}_{}.summary".format(args.patient, args.mvt)
    if args.out_dir:
        dest_path = os.path.join(args.out_dir, dest_path)
    _log.info('Write file ' + dest_path)
    with open(dest_path, 'w') as f:
        print('# Activation ratio summary', file=f)
        print("# mvt = {} files= {}".format(args.mvt,
                                            ' '.join([os.path.basename(p) for p in args.sum_path])),
              file=f)
        print("# active muscles = {}".format(' '.join(args.active)), file=f)
        print("# inactive muscles = {}".format(' '.join(args.inactive)), file=f)
        print("# {}".format(" ".join(sys.argv)), file=f)
        desc.to_csv(path_or_buf=f,
                    sep='\t',
                    float_format='%.3f',
                    na_rep='NaN')
    ave_active = desc.loc['mean', args.active]
    std_active = desc.loc['std', args.active]
    ave_inactive = desc.loc['mean', args.inactive]
    std_inactive = desc.loc['std', args.inactive]

    for state in ('active', 'inactive'):
        fig_name = "{}_{}_{}.{}".format(args.patient, args.mvt, state, 'png')
        transtab = str.maketrans('/ :', '___')
        fig_name = fig_name.translate(transtab)
        _log.info("Compute figure: " + fig_name)

        fig, ax = plt.subplots()
        ave = locals()['ave_{}'.format(state)]
        std = locals()['std_{}'.format(state)]
        ax.bar(np.arange(len(ave)),
               ave,
               yerr=std)
        ax.set_ylim([0, 1])
        ax.set_ylabel('Activation ratio')
        ax.set_xlabel('Muscles')
        ax.set_xticklabels([''] + getattr(args, state))

        if args.out_dir:
            dest_file = os.path.join(args.out_dir, fig_name)
        else:
            dest_file = fig_name
        fig.savefig(dest_file)

if __name__ == '__main__':
    main()
