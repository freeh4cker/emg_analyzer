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
import matplotlib.pyplot as plt

import emg_analyzer
from emg_analyzer.block import parse_block_def
from emg_analyzer import argparse_utils
from emg_analyzer.utils import  get_version_message



def main(args=None):
    """

    :param args:
    :return:
    """
    args = sys.argv[1:] if args is None else args

    parser = argparse.ArgumentParser(description="""Extract frame from emt as describe in block file (.blk) 
    and perform average or boxplot""")

    parser.add_argument('block_file',
                        help="The path to block file (.blk).")
    action = parser.add_mutually_exclusive_group(required=True)
    action.add_argument('--box-plot',
                        action='store_true',
                        help='create a boxplot with data. all trials are concatenate')
    action.add_argument('--average-plot',
                        action='store_true',
                        help='create a average plot between the different trials.'
                             'the original data are interpolate to have the same data number between trials.')
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

    with open(args.block_file) as blk_file:
        trials = parse_block_def(blk_file)
    if args.box_plot:
        boxplot(trials)
    elif args.average_plot
        average_plot(trials)
    else:
        assert False, "Unknown action"


def boxplot(trials):
    for bh in zip(*trials):
        for blocks in zip(*bh):
            #concatane the blocks vertically
            data = pd.concat(*blocks, axis=0, ignore_index=True)
    # save intermediate file ?
    fig = plt.figure()
    plt.boxplot(data, notch=0, sym='')
    plt.show()


def average_plot(trials):
    pass



if __name__ == '__main__':
    main()
