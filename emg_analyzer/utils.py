##########################################################################
# Copyright (c) 2017-2018 Bertrand Néron. All rights reserved.                #
# Use of this source code is governed by a BSD-style license that can be #
# found in the LICENSE file.                                             #
##########################################################################

import os
import sys

import colorlog
_log = colorlog.getLogger(__name__)

from emg_analyzer import emg


def get_version_message():
    import emg_analyzer
    import pandas
    import numpy
    version_text = """emg_group_tracks: {emg_vers}

Using: 
    - pandas: {pd_vers}
    - numpy: {np_vers}
    - python: {py_vers}""".format(emg_vers=emg_analyzer.__version__,
                                  pd_vers=pandas.__version__,
                                  np_vers=numpy.__version__,
                                  py_vers='.'.join([str(i) for i in sys.version_info[0:3]]))
    return version_text


def process_one_emt_file(emt_path, method_name, method_args, method_kwargs, dest='', suffix=''):
    """

    :param emt_path: the path of the emt file to process.
    :param str method_name: the name of the method to apply on the :class:`emg.Emg` object.
    :param tuple method_args: the args to pass to the method.
    :param dict method_kwargs: the keywords args to pass to the method.
    :param dtr dest: the directory to put the normalized file,
                     default is current working directory.
    :param suffix: the suffix to postpend to the file.
    :return: the path to the processed file.
    :rtype: str
    """
    my_emg = emg.Emg()
    with open(emt_path) as emg_file:
        my_emg.parse(emg_file)

    processed_emg = getattr(my_emg, method_name)(*method_args, **method_kwargs)

    root_dir, basename = os.path.split(emt_path)
    processed_filename, ext = os.path.splitext(basename)
    processed_filename = processed_filename.replace(' ', '_')
    processed_filename = "{base}_{suff}{ext}".format(base=processed_filename,
                                                     suff=suffix,
                                                     ext=ext)
    processed_path = os.path.join(dest, processed_filename)

    with open(processed_path, 'w') as processed_file:
        processed_emg.to_emt(file=processed_file)
    return processed_path


def process_dir(path, method_name, method_args, method_kwargs, dest='', suffix=''):
    """
    walk recursively through path and process each .emt file
    the results are write in a new tree file postpend with suffix.

    :param str path: the path of the emt file/dir to process.
    :param str method_name: the name of the method to apply on the :class:`emg.Emg` object.
    :param tuple method_args: the args to pass to the method.
    :param dict method_kwargs: the keywords args to pass to the method
    :param str dest: the directory to write down the normalized file.
    :param str suffix: the suffix to postpend to the path last element.
    :return: the path to the processed directory
    :rtype: str
    """
    path = path.rstrip(os.sep)
    root_dir, basename = os.path.split(path)
    norm_dir = "{}_{}".format(basename.replace(' ', '_'), suffix)
    if dest:
        processed_path = os.path.join(dest, norm_dir)
    else:
        processed_path = os.path.join(root_dir, norm_dir)
    if os.path.exists(processed_path):
        _log.error("directory '{}' already exists, remove it.".format(processed_path))
        raise IOError("directory exists: {}".format(processed_path))

    os.mkdir(processed_path)
    with os.scandir(path) as dir_it:
        for entry in dir_it:
            if not entry.name.startswith('.') and entry.is_file() and entry.name.endswith('.emt'):
                _log.info("Processing " + entry.path)
                process_one_emt_file(entry.path, method_name, method_args, method_kwargs, dest=processed_path, suffix=suffix)
            elif entry.is_dir():
                process_dir(entry.path, method_name, method_args, method_kwargs, dest=processed_path, suffix=suffix)
    return processed_path
