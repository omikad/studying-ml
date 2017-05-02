import numpy as np
import unittest

from mygym.approach3.receptive_field import ReceptiveField


class ReceptiveFieldTester(unittest.TestCase):
    def test_get_line(self):
        cves = [([0, 1, 2, 3], 10, [20, 21, 22, 23, 24, 25])]

        np.testing.assert_array_equal(
            [[0, 1, 2, 3, 10]],
            ReceptiveField([(0, 5)], []).get_input(cves, None, None))

        np.testing.assert_array_equal(
            [[0, 1, 2, 3]],
            ReceptiveField([(0, 4)], []).get_input(cves, None, None))

        np.testing.assert_array_equal(
            [[0, 1, 2]],
            ReceptiveField([(0, 3)], []).get_input(cves, None, None))

        np.testing.assert_array_equal(
            [[1, 2, 3]],
            ReceptiveField([(1, 3)], []).get_input(cves, None, None))

        np.testing.assert_array_equal(
            [[2, 3, 10]],
            ReceptiveField([(2, 3)], []).get_input(cves, None, None))

    def test_get_few_output_rows(self):
        cves = [([0, 1, 2, 3], 10, [20, 21, 22, 23, 24, 25]),
                ([4, 5, 6, 7], 11, [26, 27, 28, 29, 30, 31])]

        np.testing.assert_array_equal(
            [[0, 1, 2, 3, 10], [4, 5, 6, 7, 11]],
            ReceptiveField([(0, 5)], []).get_input(cves, None, None))

        np.testing.assert_array_equal(
            [[1, 2, 3, 10], [5, 6, 7, 11]],
            ReceptiveField([(1, 4)], []).get_input(cves, None, None))

    def test_get_few_lines(self):
        cves = [([0, 1, 2, 3], 10, [20, 21, 22, 23, 24, 25]),
                ([4, 5, 6, 7], 11, [26, 27, 28, 29, 30, 31])]

        np.testing.assert_array_equal(
            [[0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [4, 5, 6, 7, 11, 0, 1, 2, 3, 10]],
            ReceptiveField([(0, 5), (0, 5)], []).get_input(cves, None, None))

        np.testing.assert_array_equal(
            [[0, 0, 0, 0, 0, 0], [5, 6, 7, 11, 2, 3]],
            ReceptiveField([(1, 4), (2, 2)], []).get_input(cves, None, None))

    def test_complex_lines(self):
        cves = [([0, 1, 2, 3], 100, [20, 21, 22, 23, 24, 25]),
                ([4, 5, 6, 7], 101, [26, 27, 28, 29, 30, 31]),
                ([8, 9, 10, 11], 102, [32, 33, 34, 35, 36, 37]),
                ([12, 13, 14, 15], 103, [38, 39, 40, 41, 42, 43])]

        np.testing.assert_array_equal(
            [[0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0], [12, 9, 10, 6, 7, 101, 100]],
            ReceptiveField([(0, 1), (1, 2), (2, 3), (4, 1)], []).get_input(cves, None, None))

        np.testing.assert_array_equal(
            [[0, 0, 0, 0, 0, 0, 0], [6, 7, 101, 1, 2, 3, 100], [10, 11, 102, 5, 6, 7, 101], [14, 15, 103, 9, 10, 11, 102]],
            ReceptiveField([(2, 3), (1, 4)], []).get_input(cves, None, None))

    def test_oracles_simple(self):
        cves = [([0, 1, 2, 3], 10, [20, 21, 22, 23, 24, 25]),
                ([4, 5, 6, 7], 11, [26, 27, 28, 29, 30, 31])]

        oracles = ['alpha', 'beta', 'gamma']
        oracle_indexes = {oracles[i]: i for i in range(len(oracles))}

        oracle_predictions = np.array([[500, 501, 502], [503, 504, 505]])

        np.testing.assert_array_equal(
            [[2, 3, 10, 502, 501], [6, 7, 11, 505, 504]],
            ReceptiveField([(2, 3)], ['gamma', 'beta']).get_input(cves, oracle_predictions, oracle_indexes))

    def test_oracles_complex(self):
        cves = [([0, 1, 2, 3], 100, [20, 21, 22, 23, 24, 25]),
                ([4, 5, 6, 7], 101, [26, 27, 28, 29, 30, 31]),
                ([8, 9, 10, 11], 102, [32, 33, 34, 35, 36, 37]),
                ([12, 13, 14, 15], 103, [38, 39, 40, 41, 42, 43])]

        oracles = ['alpha', 'beta', 'gamma']
        oracle_indexes = {oracles[i]: i for i in range(len(oracles))}

        oracle_predictions = np.array([[500, 501, 502], [503, 504, 505], [506, 507, 508], [509, 510, 511]])

        np.testing.assert_array_equal(
            [[0, 0, 0, 0, 0, 0], [4, 5, 3, 100, 505, 504], [8, 9, 7, 101, 508, 507], [12, 13, 11, 102, 511, 510]],
            ReceptiveField([(0, 2), (3, 2)], ['gamma', 'beta']).get_input(cves, oracle_predictions, oracle_indexes))


if __name__ == '__main__':
    unittest.main()
