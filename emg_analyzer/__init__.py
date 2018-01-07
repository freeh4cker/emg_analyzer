##########################################################################
# Copyright (c) 2017-2018 Bertrand Néron. All rights reserved.                #
# Use of this source code is governed by a BSD-style license that can be #
# found in the LICENSE file.                                             #
##########################################################################
import colorlog

__version__ = '0.1b'


def init_logger():
    handler = colorlog.StreamHandler()
    formatter = colorlog.ColoredFormatter("%(log_color)s%(levelname)-8s : %(message)s %(reset)s",
                                          datefmt=None,
                                          reset=False,
                                          log_colors={
                                              'DEBUG':    'cyan',
                                              'INFO':     'green',
                                              'WARNING':  'yellow',
                                              'ERROR':    'red',
                                              'CRITICAL': 'bold_red',
                                          },
                                          secondary_log_colors={},
                                          style='%'
                                          )
    handler.setFormatter(formatter)
    logger = colorlog.getLogger('emg_analyzer')
    logger.addHandler(handler)
    logger.setLevel(colorlog.logging.logging.WARNING)


init_logger()

def logger_set_level(level=colorlog.logging.logging.WARNING):
    assert level in (colorlog.logging.logging.DEBUG,
                     colorlog.logging.logging.INFO,
                     colorlog.logging.logging.WARNING,
                     colorlog.logging.logging.ERROR,
                     colorlog.logging.logging.CRITICAL)
    logger = colorlog.getLogger('emg_analyzer')
    if level <= colorlog.logging.logging.DEBUG:
        formatter = colorlog.ColoredFormatter(
            "%(log_color)s%(levelname)-8s : %(module)s: L %(lineno)d :%(reset)s %(message)s",
            datefmt=None,
            reset=False,
            log_colors={
                'DEBUG': 'cyan',
                'INFO': 'green',
                'WARNING': 'yellow',
                'ERROR': 'red',
                'CRITICAL': 'bold_red',
            },
            secondary_log_colors={},
            style='%'
            )
        handler = logger.handlers[0]
        handler.setFormatter(formatter)

    logger.setLevel(level)
