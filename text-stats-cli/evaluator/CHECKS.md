# Acceptance checks — 1.0.0

Evaluator-only: do not send this file, checker source, or reference code to the
model. Send only the generated feedback block. All eight checks have equal weight.
Each check passes only if all its cases pass, including subprocess exit status and
output validation. A crash or timeout fails the affected check; other checks run.

| ID | Requirement exercised |
|---|---|
| CLI-01 | Default stdin, ordinary text, tabs, JSON shape and integer types, successful exit, no stderr, deterministic output |
| CLI-02 | LF counting: blank lines, terminal LF, no terminal LF, CRLF, lone CR |
| CLI-03 | Code points vs bytes, combining characters, Unicode whitespace, BOM preservation, whitespace-only input |
| CLI-04 | Empty stdin and empty file |
| CLI-05 | Files with spaces or option-like names, stdin ignored, CRLF preserved, file unchanged |
| CLI-06 | Explicit `-` for nonempty and empty stdin |
| CLI-07 | Missing file, directory path, malformed UTF-8 from stdin and file |
| CLI-08 | Multiple arguments, including `-` followed by an extra argument |

Expected values are literal, hand-computed values, not imported from the reference
solution. The reference and deliberate defects are checked by `verify.py`.

Checks intentionally overlap on the CLI/output contract: a broken interface can
make every requirement unobservable. These are functional requirement scores, not
independent statistical measurements. No finite suite proves correctness for all
possible input; side effects beyond the checked input files are not audited.

The checker normalizes failures into fixed messages: it discloses neither raw
tracebacks nor case-specific expected values. Feedback is in ascending check-ID
order. There is no raw-log truncation policy to apply because no raw log is sent.
