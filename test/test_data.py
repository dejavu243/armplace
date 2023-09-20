"""Tests for Grinev algorithm"""
import logging
import unittest

import data.right_hand_70kg.right_hand_70kg as rh70
import data.left_hand_75kg.left_hand_75kg as lh75
import data.left_hand_80kg.left_hand_80kg as lh80

data_test = [lh80, lh75, rh70]

logger = logging.getLogger("test")


def check_pairs_names(_names: dict, _pairs: list) -> bool:
    unmapped_names = []
    for index, pair in enumerate(_pairs):
        check_condition = (pair[0] not in _names.values() or pair[1] not in _names.values()) \
                          and "" not in pair
        if check_condition:
            unmapped_names.append(pair)
            logger.warning("Some name in pair %s  wit index %d is not in initial table names",
                           pair, index)
    return not unmapped_names


class TestData(unittest.TestCase):
    def test_pairs_names(self):
        for data in data_test:
            self.assertTrue(check_pairs_names(data.names, data.pairs))

    def test_weights_names(self):
        for data in data_test:
            if data.weights:
                for name in data.names.values():
                    self.assertTrue(name in data.weights.keys())
