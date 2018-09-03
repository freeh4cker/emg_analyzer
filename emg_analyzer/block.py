##########################################################################
# Copyright (c) 2017-2018 Bertrand Néron. All rights reserved.           #
# Use of this source code is governed by a BSD-style license that can be #
# found in the LICENSE file.                                             #
##########################################################################

import os
import colorlog

_log = colorlog.getLogger('emg_analyzer.block')

from emg_analyzer.emg import Emg


class Block:
    """
    A *Block* handle a reference to the emt file and position start and stop (included) of the
    block of data to extract
    """
    def __init__(self, ref, nb,  start, stop):
        self.ref = ref
        self.nb = nb
        self.start = start
        self.stop = stop

    def __eq__(self, other):
        return self.ref == other.ref and \
               self.nb == other.nb and \
               self.start == other.start and \
               self.stop == other.stop

    def __str__(self):
        return """ref = {}
nb = {}
start = {}
stop = {}""".format(self.ref, self.nb, self.start, self.stop)

    def get_data(self):
        """

        :return: The data extracted from the reference from the frame *start* to *stop* (included)
                 The time column has been discarded.
        :rtype: :class:`pandas.DataFrame` object.
        """
        # parse emt
        # extract only lines corresponding to block
        emg = Emg()
        with open(self.ref) as emt:
            emg.parse(emt)
        emg_data = emg.data
        data = emg_data.get_frames(self.start, self.stop)
        data = data.drop(['Time'], axis=1)
        return data
    

class BlockHandler:
    """
    A BlockHandler handle a serie of block which shared the same reference
    """

    def __init__(self, ref):
        self.ref = ref
        self.blocks = []

    def add_block(self, block):
        self.blocks.append(block)

    def __iter__(self):
        generator = (block for block in sorted(self.blocks, key=lambda blk: blk.nb))
        return generator


def parse_block_def(block_file, sep):
    """
    parse a block defition file and return a list of :class:`BlockHandler` objects.
    :param block_file: The definition block file to parse
    :type block_file: file object
    :return: list of :class:`BlockHandler` objects.
    """
    block_handlers = []
    current_block_handler = None
    for line in block_file:
        line = line.strip()
        if not line:
            continue
        elif line.startswith('#'):
            continue
        elif line.lower().startswith('file'):
            if current_block_handler:
                #  start a new trial so add the current block handler to trials before to init a new one
                block_handlers.append(current_block_handler)
            line = line.strip(sep)
            ref = line.split(':')[1].strip()
            ref = os.path.normpath(os.path.join(os.path.dirname(block_file.name), ref))
            if not os.path.exists(ref):
                msg = 'File not found: {}'.format(ref)
                _log.critical(msg)
                raise IOError(msg)
            current_block_handler = BlockHandler(ref)
        else:
            try:
                block_nb, start, stop, *_ = line.split(sep)
                if not any([start, stop]):
                    continue
                block_nb = int(block_nb.strip())
                start = int(start.strip())
                stop = int(stop.strip())
            except Exception as err:
                raise RuntimeError("{}: {}".format(line, err))
            current_block_handler.add_block(Block(ref, block_nb, start, stop))
    # This is the end of the file so add the current block handler to the trials
    block_handlers.append(current_block_handler)
    return block_handlers
