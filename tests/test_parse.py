"""Tests for fmproof.semver.parse."""

import unittest

from fmproof.semver import InvalidVersionError, Version, is_numeric_identifier, parse


class ParseValidTest(unittest.TestCase):
    def test_version_core(self):
        self.assertEqual(parse("1.2.3"), Version(1, 2, 3, ()))

    def test_all_zero(self):
        self.assertEqual(parse("0.0.0"), Version(0, 0, 0, ()))

    def test_large_numbers(self):
        self.assertEqual(parse("10.20.30"), Version(10, 20, 30, ()))

    def test_single_prerelease_identifier(self):
        self.assertEqual(parse("1.0.0-alpha"), Version(1, 0, 0, ("alpha",)))

    def test_dotted_prerelease(self):
        self.assertEqual(parse("1.0.0-alpha.1"), Version(1, 0, 0, ("alpha", "1")))

    def test_numeric_prerelease_identifier_kept_as_string(self):
        self.assertEqual(parse("1.0.0-0.3.7").prerelease, ("0", "3", "7"))

    def test_hyphen_in_prerelease(self):
        self.assertEqual(parse("1.0.0-x-y-z.-").prerelease, ("x-y-z", "-"))


class ParseInvalidTest(unittest.TestCase):
    def test_build_metadata_rejected(self):
        with self.assertRaises(InvalidVersionError):
            parse("1.0.0+build.5")

    def test_prerelease_with_build_metadata_rejected(self):
        with self.assertRaises(InvalidVersionError):
            parse("1.0.0-alpha+001")

    def test_partial_version_rejected(self):
        with self.assertRaises(InvalidVersionError):
            parse("1.2")

    def test_leading_v_rejected(self):
        with self.assertRaises(InvalidVersionError):
            parse("v1.2.3")

    def test_leading_zero_rejected(self):
        with self.assertRaises(InvalidVersionError):
            parse("01.2.3")

    def test_leading_zero_in_numeric_prerelease_rejected(self):
        with self.assertRaises(InvalidVersionError):
            parse("1.0.0-01")

    def test_empty_prerelease_rejected(self):
        with self.assertRaises(InvalidVersionError):
            parse("1.0.0-")

    def test_whitespace_rejected(self):
        with self.assertRaises(InvalidVersionError):
            parse(" 1.2.3 ")

    def test_non_string_rejected(self):
        with self.assertRaises(InvalidVersionError):
            parse(123)

    def test_error_is_a_value_error(self):
        self.assertTrue(issubclass(InvalidVersionError, ValueError))


class NumericIdentifierTest(unittest.TestCase):
    def test_digits_are_numeric(self):
        self.assertTrue(is_numeric_identifier("0"))
        self.assertTrue(is_numeric_identifier("42"))

    def test_alphanumeric_is_not_numeric(self):
        self.assertFalse(is_numeric_identifier("alpha"))
        self.assertFalse(is_numeric_identifier("1a"))
        self.assertFalse(is_numeric_identifier("-"))


class StrTest(unittest.TestCase):
    def test_round_trip_release(self):
        self.assertEqual(str(parse("1.2.3")), "1.2.3")

    def test_round_trip_prerelease(self):
        self.assertEqual(str(parse("1.0.0-alpha.1")), "1.0.0-alpha.1")


if __name__ == "__main__":
    unittest.main()
