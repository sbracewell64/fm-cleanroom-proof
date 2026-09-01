# fm-cleanroom-proof

A clean-room proof repository. It exists to carry exactly one candidate change
along the path

    correct code -> green exact-head PR -> objectively mergeable
                 -> expected-head protected merge -> observed merged state
                 -> machine-readable disposition

so that every precondition of the landing is observable after the fact from a
record, and the final gate is enforced by a server rather than by a rule an
agent was told to follow.

The library under `fmproof/` is a deliberately small SemVer 2.0.0 helper. Its
content is a vehicle: the proof is about the path, not the parser.

## Layout

| Path | What it is |
|---|---|
| `fmproof/semver.py` | SemVer 2.0.0 parsing, and version precedence comparison |
| `tests/` | `unittest` suite, run by both CI and the pipeline's test step |
| `.no-mistakes.yaml` | pipeline commands, read only from the trusted default-branch copy |
| `.github/workflows/ci.yml` | the `test` required status check |
| `.github/workflows/no-mistakes-required.yml` | the `PR must be raised via no-mistakes` required status check |

## Running the tests

    python3 -m unittest discover -s tests -t . -v

## How changes land here

`main` is protected: `enforce_admins` is on, both status checks above are
required, and force-pushes and deletions are refused. Squash and rebase merges
are disabled, so every landing is a true merge commit whose second parent is
exactly the head that was authorized. Direct pushes to `main` are not part of
the workflow; the single seed commit predates protection and is recorded as a
one-commit bootstrap exception.
