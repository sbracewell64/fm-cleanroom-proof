"""SemVer 2.0.0 parsing and precedence comparison.

This module is deliberately strict. It accepts exactly the grammar in the
SemVer 2.0.0 specification for a version *core* plus an optional pre-release,
and rejects everything else - including build metadata, which the specification
allows syntactically (SemVer 2.0.0 section 10) but which this module does not
support.

Rejecting rather than ignoring build metadata is a choice: a caller who passes
``1.0.0+build.5`` almost certainly cares about that suffix, and silently
discarding it would answer a question the caller did not ask.

Precedence comparison follows SemVer 2.0.0 section 11 exactly, and is built
on :func:`parse`, so a string this module will not parse is a string it will
not compare either.
"""

from __future__ import annotations

import re
from typing import NamedTuple, Tuple

__all__ = ["Version", "InvalidVersionError", "parse", "compare"]

# A numeric identifier is 0, or a non-zero digit followed by digits: no leading
# zeroes (SemVer 2.0.0 section 9).
_NUMERIC_IDENTIFIER = r"0|[1-9]\d*"

# An alphanumeric identifier contains at least one non-digit, so that it can
# never also be read as a numeric identifier.
_ALPHANUMERIC_IDENTIFIER = r"\d*[A-Za-z-][0-9A-Za-z-]*"

_PRERELEASE_IDENTIFIER = f"(?:{_ALPHANUMERIC_IDENTIFIER}|{_NUMERIC_IDENTIFIER})"

_VERSION_RE = re.compile(
    r"^"
    rf"(?P<major>{_NUMERIC_IDENTIFIER})"
    rf"\.(?P<minor>{_NUMERIC_IDENTIFIER})"
    rf"\.(?P<patch>{_NUMERIC_IDENTIFIER})"
    rf"(?:-(?P<prerelease>{_PRERELEASE_IDENTIFIER}(?:\.{_PRERELEASE_IDENTIFIER})*))?"
    r"$"
)

_DIGITS_RE = re.compile(r"^\d+$")


class InvalidVersionError(ValueError):
    """Raised when a string is not a version this module accepts."""


class Version(NamedTuple):
    """A parsed version.

    ``prerelease`` is the tuple of dot-separated pre-release identifiers, empty
    for a release version. Identifiers are kept as strings; whether one is
    numeric is a property of its characters and is decided where it matters.
    """

    major: int
    minor: int
    patch: int
    prerelease: Tuple[str, ...] = ()

    def __str__(self) -> str:
        core = f"{self.major}.{self.minor}.{self.patch}"
        if not self.prerelease:
            return core
        return core + "-" + ".".join(self.prerelease)


def is_numeric_identifier(identifier: str) -> bool:
    """Whether a pre-release identifier is numeric.

    The grammar guarantees a numeric identifier carries no leading zero, so an
    all-digits identifier is numeric and anything else is alphanumeric.
    """
    return bool(_DIGITS_RE.match(identifier))


def parse(version: str) -> Version:
    """Parse ``version`` into a :class:`Version`.

    Raises :class:`InvalidVersionError` for anything outside the accepted
    grammar, including build metadata, a leading ``v``, surrounding whitespace,
    a partial version such as ``1.2``, and a numeric part with a leading zero.
    """
    if not isinstance(version, str):
        raise InvalidVersionError(f"version must be a string, got {type(version).__name__}")

    match = _VERSION_RE.match(version)
    if match is None:
        raise InvalidVersionError(f"not a valid version: {version!r}")

    prerelease = match.group("prerelease")
    return Version(
        major=int(match.group("major")),
        minor=int(match.group("minor")),
        patch=int(match.group("patch")),
        prerelease=tuple(prerelease.split(".")) if prerelease else (),
    )


def _compare_identifiers(left: str, right: str) -> int:
    """Compare two pre-release identifiers (SemVer 2.0.0 section 11.4.1-11.4.3)."""
    left_numeric = is_numeric_identifier(left)
    right_numeric = is_numeric_identifier(right)

    if left_numeric and right_numeric:
        # 11.4.1: identifiers consisting only of digits are compared numerically.
        return _sign(int(left) - int(right))
    if left_numeric != right_numeric:
        # 11.4.3: numeric identifiers always have lower precedence than
        # alphanumeric ones.
        return -1 if left_numeric else 1
    # 11.4.2: identifiers with letters or hyphens are compared lexically in
    # ASCII sort order.
    return _sign((left > right) - (left < right))


def _sign(value: int) -> int:
    if value < 0:
        return -1
    return 1 if value > 0 else 0


def compare(a: str, b: str) -> int:
    """Compare two versions by SemVer 2.0.0 precedence.

    Returns ``-1`` when ``a`` has lower precedence than ``b``, ``1`` when it has
    higher, and ``0`` when the two have equal precedence.

    Both arguments go through :func:`parse`, so an input outside the accepted
    grammar - build metadata included - raises :class:`InvalidVersionError`
    rather than being compared on a guess.
    """
    left = parse(a)
    right = parse(b)

    # 11.2: major, minor and patch are compared numerically, in that order.
    core = _sign(
        (left.major, left.minor, left.patch) > (right.major, right.minor, right.patch)
    ) - _sign(
        (left.major, left.minor, left.patch) < (right.major, right.minor, right.patch)
    )
    if core:
        return core

    # 11.3: when the version core is equal, a pre-release version has lower
    # precedence than the associated release version.
    if not left.prerelease and not right.prerelease:
        return 0
    if not left.prerelease:
        return 1
    if not right.prerelease:
        return -1

    # 11.4: compare each dot-separated identifier from left to right until a
    # difference is found.
    for left_id, right_id in zip(left.prerelease, right.prerelease):
        result = _compare_identifiers(left_id, right_id)
        if result:
            return result

    # 11.4.4: a larger set of pre-release fields has higher precedence than a
    # smaller set, when all of the preceding identifiers are equal.
    return _sign(len(left.prerelease) - len(right.prerelease))
