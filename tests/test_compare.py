"""Tests for fmproof.semver.compare (SemVer 2.0.0 section 11 precedence)."""

import unittest

from fmproof.semver import InvalidVersionError, compare


class CoreOrderingTest(unittest.TestCase):
    """Section 11.2: major, minor and patch compared numerically, in order."""

    def test_major_dominates(self):
        self.assertEqual(compare("1.0.0", "2.0.0"), -1)
        self.assertEqual(compare("2.0.0", "1.0.0"), 1)

    def test_minor_breaks_equal_major(self):
        self.assertEqual(compare("2.0.0", "2.1.0"), -1)

    def test_patch_breaks_equal_major_minor(self):
        self.assertEqual(compare("2.1.0", "2.1.1"), -1)

    def test_equal_cores(self):
        self.assertEqual(compare("1.2.3", "1.2.3"), 0)

    def test_numeric_not_lexical(self):
        self.assertEqual(compare("2.0.0", "10.0.0"), -1)

    def test_specification_example_chain(self):
        chain = ["1.0.0", "2.0.0", "2.1.0", "2.1.1"]
        for lower, higher in zip(chain, chain[1:]):
            self.assertEqual(compare(lower, higher), -1)
            self.assertEqual(compare(higher, lower), 1)


class PrereleaseVersusReleaseTest(unittest.TestCase):
    """Section 11.3: a pre-release version sorts below its release."""

    def test_prerelease_is_lower(self):
        self.assertEqual(compare("1.0.0-alpha", "1.0.0"), -1)

    def test_release_is_higher(self):
        self.assertEqual(compare("1.0.0", "1.0.0-alpha"), 1)

    def test_prerelease_does_not_leak_across_cores(self):
        self.assertEqual(compare("1.0.0", "1.0.1-alpha"), -1)


class PrereleaseIdentifierTest(unittest.TestCase):
    """Section 11.4.1-11.4.3: identifier-by-identifier comparison."""

    def test_numeric_identifiers_compare_numerically(self):
        self.assertEqual(compare("1.0.0-2", "1.0.0-10"), -1)

    def test_alphanumeric_identifiers_compare_lexically(self):
        self.assertEqual(compare("1.0.0-alpha", "1.0.0-beta"), -1)

    def test_numeric_is_lower_than_alphanumeric(self):
        self.assertEqual(compare("1.0.0-1", "1.0.0-alpha"), -1)
        self.assertEqual(compare("1.0.0-alpha", "1.0.0-1"), 1)

    def test_equal_prereleases(self):
        self.assertEqual(compare("1.0.0-alpha.1", "1.0.0-alpha.1"), 0)

    def test_ascii_order_puts_uppercase_first(self):
        self.assertEqual(compare("1.0.0-RC", "1.0.0-rc"), -1)


class PrereleaseFieldCountTest(unittest.TestCase):
    """Section 11.4.4: with an equal prefix, more fields sorts higher."""

    def test_longer_prerelease_with_equal_prefix_is_higher(self):
        self.assertEqual(compare("1.0.0-alpha", "1.0.0-alpha.1"), -1)
        self.assertEqual(compare("1.0.0-alpha.1", "1.0.0-alpha"), 1)

    def test_difference_before_the_end_wins_over_length(self):
        self.assertEqual(compare("1.0.0-alpha.beta", "1.0.0-alpha.1.1"), 1)


class SpecificationExampleTest(unittest.TestCase):
    """The full ordering published in SemVer 2.0.0 section 11.4."""

    ORDER = [
        "1.0.0-alpha",
        "1.0.0-alpha.1",
        "1.0.0-alpha.beta",
        "1.0.0-beta",
        "1.0.0-beta.2",
        "1.0.0-beta.11",
        "1.0.0-rc.1",
        "1.0.0",
    ]

    def test_each_adjacent_pair_ascends(self):
        for lower, higher in zip(self.ORDER, self.ORDER[1:]):
            self.assertEqual(compare(lower, higher), -1, f"{lower} < {higher}")
            self.assertEqual(compare(higher, lower), 1, f"{higher} > {lower}")

    def test_sorting_reproduces_the_published_order(self):
        import functools
        shuffled = list(reversed(self.ORDER))
        self.assertEqual(sorted(shuffled, key=functools.cmp_to_key(compare)), self.ORDER)

    def test_every_version_equals_itself(self):
        for version in self.ORDER:
            self.assertEqual(compare(version, version), 0)


class RejectedInputTest(unittest.TestCase):
    """compare() is built on parse(), so it rejects what parse() rejects."""

    def test_build_metadata_raises(self):
        with self.assertRaises(InvalidVersionError):
            compare("1.0.0+build.5", "1.0.0")

    def test_build_metadata_on_the_right_raises(self):
        with self.assertRaises(InvalidVersionError):
            compare("1.0.0", "1.0.0+build.5")

    def test_partial_version_raises(self):
        with self.assertRaises(InvalidVersionError):
            compare("1.0", "1.0.0")

    def test_error_is_a_value_error(self):
        with self.assertRaises(ValueError):
            compare("nope", "1.0.0")


if __name__ == "__main__":
    unittest.main()
