# Text statistics CLI

A small Python build-from-specification benchmark.
**Version: 1.0.0 · Difficulty: basic · Python: 3.11+ · Checks: 8**
No third-party packages are needed by the challenge or evaluator.

## Run the experiment

1. Download or clone this repository and open the `text-stats-cli/` folder.
   All paths and commands below are relative to that folder.
   Create a run folder under `results/` (for example, `results/run-001/`).
   Copy `results/TEMPLATE.md` there and record your
   exact Python version and model setup in it.
2. Start a fresh chat with browsing, execution, and repository tools disabled.
   Disable memory/custom instructions if possible; record any exceptions.
3. Paste `model/prompt.md` and then `model/SPEC.md` as **one message**. Do not
   supply this README, scoring tests, or the reference implementation.
4. Save the response verbatim. Copy the contents of its single Python code block
   into `submission/text_stats.py` without edits (create `submission/` first).
   If there is no unambiguous single Python code block, save an empty file and
   score that attempt. Do not assemble multiple blocks or repair syntax.
5. From the `text-stats-cli/` folder, run:

   ```sh
   python3 evaluator/check.py submission/text_stats.py --round 1
   ```

6. Save the entire checker output. If checks fail, send **only the text between
   BEGIN FEEDBACK and END FEEDBACK** to the same conversation. Copy the full
   replacement code into the submission file and run the same command with
   `--round 2`.
7. If failures remain, send that second feedback message, replace the code, and
   run the checker with `--round 0` (score only). No further correction is allowed.
8. Stop early on 8/8. Save each response, feedback message, candidate file, and
   checker output alongside the completed run record.

The checker exit code is 0 for a full pass, 1 for a scored failure, and 2 for an
invalid evaluator invocation. It prints all check outcomes and a requirement-level
score. Several cases may exercise one requirement; that requirement gets one point.

Generated code executes on your machine. Use a disposable environment without
credentials or sensitive files. The checker uses temporary working directories
and timeouts; it is not a security sandbox.

## Rules

- One initial attempt and at most two correction rounds; no manual fixes or hints.
- The model writes code only. The participant executes the checks externally.
- Evaluate each replacement independently, including previously passed checks.
- Clarifications, refusals, and truncated answers count as attempts. Apply the
  extraction rule and standard feedback; do not grant extra continuation turns.
- If the provider fails without producing a response, retry the exact message
  once and record it. A second failure makes the run incomplete, not a model zero.
- Missing evaluator prerequisites or an invalid candidate path are infrastructure
  errors. Candidate syntax errors, crashes, and five-second invocation timeouts
  are scored failures. Each candidate invocation gets the same timeout.
- Send only the checker's fixed feedback. Raw tracebacks, expected values, and
  hidden case inputs are withheld in this version; raw-error feedback is not used.
- Record model/setup and Python version. Treat different enabled capabilities as
  separate setup groups; report initial and assisted scores separately.
- This is a functional-correctness benchmark, not a security, performance, or
  code-quality review. The evaluator cases are public but withheld during runs.

## Maintainer verification

```sh
python3 evaluator/verify.py
```

This checks that the evaluator accepts an independently readable reference
implementation and rejects deliberate counting, input-handling, and error-handling
defects. `evaluator/reference.py` is an evaluator-only answer, not starter code.
Live cloud/local model runs are separate from this verification.

Scoring changes require a version bump. Record version and Git commit (or
`uncommitted`) with each run. Exact runtime versions matter for Unicode semantics.
