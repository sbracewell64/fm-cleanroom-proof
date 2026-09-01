"""Deliberately failing test. It exists to be watched red."""

import unittest


class DeliberateFailureTest(unittest.TestCase):
    def test_this_must_fail(self):
        self.assertEqual(1, 2, "deliberate failure for negative control NC-1")
