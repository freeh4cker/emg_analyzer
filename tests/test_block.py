##########################################################################
# Copyright (c) 2017-2018 Bertrand Néron. All rights reserved.           #
# Use of this source code is governed by a BSD-style license that can be #
# found in the LICENSE file.                                             #
##########################################################################


import pandas as pd

try:
    from tests import EmgTest
except ImportError as err:
    msg = "Cannot import emg_analyzer: {0!s}".format(err)
    raise ImportError(msg)

from emg_analyzer import block


class TestBlock(EmgTest):

    def test_Block(self):
        ref = 'toto'
        nb, start, stop = 1, 10, 20
        blk = block.Block(ref, nb, start, stop)
        self.assertEqual(blk.ref, ref)
        self.assertEqual(blk.nb, nb)
        self.assertEqual(blk.start, start)
        self.assertEqual(blk.stop, stop)

    def test_get_data(self):
        ref = self.get_data('exp1.emt')
        nb, start, stop = 1, 1, 4
        blk = block.Block(ref, nb, start, stop)
        data = blk.get_data()
        exp_data = pd.DataFrame({'A': [2.1, 3.1, 4.1, 5.1],
                                 'B': [20.1, 30.1, 40.1, 50.1]},
                                index=[1, 2, 3, 4])
        exp_data.index.name = 'Frame'
        pd.util.testing.assert_frame_equal(exp_data, data)


class TestBlockHandler(EmgTest):

    def test_BlockHandler(self):
        ref = 'foo'
        bh = block.BlockHandler(ref)
        self.assertEqual(bh.ref, ref)
        self.assertListEqual(bh.blocks, [])

    def test_add_block(self):
        ref = 'foo'
        bh = block.BlockHandler(ref)
        self.assertListEqual(bh.blocks, [])
        nb, start, stop = 1, 10, 20
        blk = block.Block(ref, nb, start, stop)
        bh.add_block(blk)
        self.assertListEqual(bh.blocks, [blk])

    def test_iter(self):
        ref = 'foo'
        bh = block.BlockHandler(ref)
        nb1, start1, stop1 = 1, 10, 20
        blk1 = block.Block(ref, nb1, start1, stop1)
        bh.add_block(blk1)
        nb2, start2, stop2 = 1, 10, 20
        blk2 = block.Block(ref, nb2, start2, stop2)
        bh.add_block(blk2)
        ctrl = [blk1, blk2]
        for b , c in zip(bh, ctrl):
            self.assertEqual(b, c)


class TestParser(EmgTest):

    def test_parse_block_def(self):
        with open(self.get_data('block_def.blk')) as blk_f:
            trials = block.parse_block_def(blk_f)
        ref = self.get_data('exp1.emt')
        bh1 = block.BlockHandler(ref)
        bh1.add_block(block.Block(ref, 1, 0, 2))
        bh1.add_block(block.Block(ref, 2, 3, 5))
        bh1.add_block(block.Block(ref, 3, 6, 8))

        ref = self.get_data('exp2.emt')
        bh2 = block.BlockHandler(ref)
        bh2.add_block(block.Block(ref, 1, 1, 4))
        bh2.add_block(block.Block(ref, 2, 4, 7))
        bh2.add_block(block.Block(ref, 3, 7, 9))

        self.assertEqual(len(trials), 2)
        for trial, bh in zip(trials, [bh1, bh2]):
            for b, ctrl in zip(trial, bh):
                self.assertEqual(b, ctrl)