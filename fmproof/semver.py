"""SemVer 2.0.0 parsing.

This module is deliberately strict. It accepts exactly the grammar in the
SemVer 2.0.0 specification for a version *core* plus an optional pre-release,
and rejects everything else - including build metadata, which the specification
allows syntactically (SemVer 2.0.0 section 10) but which this module does not
support.

Rejecting rather than ignoring build metadata is a choice: a caller who passes
``1.0.0+build.5`` almost certainly cares about that suffix, and silently
discarding it would answer a question the caller did not ask.
"""

from __future__ import annotations

import re
from typing import NamedTuple, Tuple

__all__ = ["Version", "InvalidVersionError", "parse"]

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
