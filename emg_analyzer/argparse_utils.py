##########################################################################
# Copyright (c) 2017-2018 Bertrand Néron. All rights reserved.                #
# Use of this source code is governed by a BSD-style license that can be #
# found in the LICENSE file.                                             #
##########################################################################


import argparse


class VersionAction(argparse._VersionAction):
    """Class to allow argparse to handel more complex version output"""

    def __call__(self, parser, namespace, values, option_string=None):
        """Override the :meth:`argparse._VersionAction.__call__` to use
           a RawTextHelpFormatter only for version action whatever the class_formatter
           specified for the :class:`argparse.ArgumentParser` object.
        """
        version = self.version
        if version is None:
            version = parser.version
        formatter = argparse.RawTextHelpFormatter(parser.prog)
        formatter.add_text(version)
        parser._print_message(formatter.format_help(), argparse._sys.stdout)
        parser.exit()


