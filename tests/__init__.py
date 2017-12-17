import os
import unittest


class EmgTest(unittest.TestCase):

    _data_dir = os.path.normpath(os.path.join(os.path.dirname(__file__), "data"))

    def get_data(self, path):
        data_path = os.path.join(self._data_dir, path)
        if not os.path.exists(data_path):
            raise FileNotFoundError("{} not found".format(data_path))
        return data_path
