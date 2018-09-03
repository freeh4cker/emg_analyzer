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
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import scipy.interpolate

import emg_analyzer
from emg_analyzer.block import parse_block_def
from emg_analyzer import argparse_utils
from emg_analyzer.utils import get_version_message



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
    parser.add_argument('--separator',
                        default=',',
                        help="the field separator (default ',')")
    action.add_argument('--box-plot',
                        action='store_true',
                        help='create a boxplot with data. all trials are concatenate')
    action.add_argument('--mean-plot',
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
        trials = parse_block_def(blk_file, args.separator)
    exp_name = os.path.basename(args.block_file)
    exp_name = os.path.splitext(exp_name)[0]
    out_fig_dir_name = '{}_figs'.format(exp_name)
    os.mkdir(out_fig_dir_name)
    if args.box_plot:
        boxplot(trials, exp_name, out_fig_dir_name)
    elif args.mean_plot:
        average_plot(trials, exp_name, out_fig_dir_name)
    else:
        assert False, "Unknown action"


def boxplot(trials, try_name, out_dir_name):
    # a trial is BlockHandler
    for i, blocks in enumerate(zip(*trials), 1):
        # concatenate the blocks vertically
        trials = [b.get_data() for b in blocks]
        # concatenate the trials vertically
        muscles = pd.concat(trials, axis=0, ignore_index=True, sort=False)
        # save intermediate file ?
        boxplot_muscles(muscles,
                        os.path.join(out_dir_name, "{}_block_{}".format(try_name, i)),
                        title='Comparison of muscles for activation block {}'.format(i))
        cols_name = [os.path.splitext(os.path.basename(b.ref))[0] for b in blocks]
        for muscle in trials[0].columns:
            data = pd.concat([d[muscle] for d in trials], axis=1, ignore_index=True)
            data.columns = cols_name
            boxplot_trials(data,
                           os.path.join(out_dir_name, "{}_muscle_{}_block_{}".format(try_name, muscle, i)),
                           title='Comparison of trials for muscle {} and block {}'.format(muscle, i))


def boxplot_muscles(data, fig_path, title=''):
    """
    draw a boxplot with oen box by muscle, save figure in png file

    :param data: dataframe with muscles as columns and activities as rows
    :param str fig_path: the path of the figure
    :param str title: the figure title
    """
    plt.close('all')
    fig, ax = plt.subplots()
    ax.boxplot(data.T, notch=0, sym='')
    ax.set_xticklabels(list(data.columns))
    ax.set_title(title)
    plt.tight_layout()
    fig.savefig(fig_path)


def boxplot_trials(data, fig_path, title=''):
    """
    draw a boxplot with one box by trial, save figure in png file.

    :param data: dataframe with trials as columns and activities as rows
    :type data: :class:`pandas.DataFrame` object
    :param str fig_path: the path of the figure
    :param str title: the figure title
    """
    plt.close('all')
    fig, ax = plt.subplots()
    trials = []
    for trial in data.columns:
        trials.append(data[trial].dropna())
    ax.boxplot(trials, notch=0, sym='')
    ax.set_xticklabels(list(data.columns), rotation=45, ha='right')
    ax.set_title(title)
    plt.tight_layout()
    fig.savefig(fig_path)


def average_plot(trials, exp_name, out_dir_name):
    all_muscles = {}
    block_size = []
    for i, blocks in enumerate(zip(*trials), 1):
        # au 1er tour
        # block_1 essai_1, block_1 essai_2 , block_1 essai_3, ...
        one_block_from_each_trial = [b.get_data() for b in blocks]
        new_size = max([len(b) for b in one_block_from_each_trial])
        block_size.append(new_size)
        for muscle in one_block_from_each_trial[0].columns:
            # ai0 block_1 essai_1, ai0 block_1 essai_2, ai0 block_1 essai_3, ...
            muscle_data = [b[muscle] for b in one_block_from_each_trial]
            simulated = []
            for trial in muscle_data:
                # ai0 block_1 essai_1
                actual_size = len(trial)
                interp_func = scipy.interpolate.interp1d(range(actual_size), trial)
                sim_muscle = interp_func(np.linspace(0, actual_size - 1, num=new_size, endpoint=True))
                simulated.append(sim_muscle)
            # concatene horizontalement
            sim_block = pd.DataFrame(simulated).T
            # moyenne de chaque row
            sim_block['mean'] = sim_block.mean(axis=1)
            if muscle in all_muscles:
                all_muscles[muscle].append(sim_block)
            else:
                all_muscles[muscle] = [sim_block]

    for muscle in all_muscles:
        # concatenate vertically the blocks
        all_block_for_one_mucle = pd.concat(all_muscles[muscle], axis=0, ignore_index=True)
        fig_path = os.path.join(out_dir_name, "{}_muscle_{}_mean".format(exp_name, muscle, i))
        title = "events for exp {} and muscle {}".format(exp_name, muscle)
        plot_data(all_block_for_one_mucle, block_size, title, fig_path)


def plot_data(data, block_size, title, fig_path):
    plt.close('all')
    colors = ['palegreen', 'skyblue', 'mediumpurple', 'gold']
    fig, ax = plt.subplots()
    fig.set_size_inches(12, 6)
    for i, col in enumerate(data.columns):
        if col == 'mean':
            color = 'red'
            label = 'mean'
        else:
            color = colors[i % len(colors)]
            label = 'trial_{}'.format(i)
        ax.plot(data[col], color=color, label=label)
    ax.legend()
    ax.set_title(title)
    x = 0
    for size in block_size:
        x += size
        ax.axvline(x=x, linestyle='dashed')
    plt.tight_layout()
    fig.savefig(fig_path)

if __name__ == '__main__':
    main()
