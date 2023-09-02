"""Tests for Grinev algorithm"""
import logging
import unittest

from data.left_hand_75kg.left_hand_75kg import names, pairs

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
        self.assertTrue(check_pairs_names(names, pairs))
