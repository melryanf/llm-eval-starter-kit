# Meeting action items

An objective, copy-and-paste language-model experiment for everyday users.
**Version: 1.0.0 · Difficulty: basic · Scoring: manual · Checks: 10**

## Run the experiment

1. Download this repository (GitHub: **Code → Download ZIP**) or clone it, then
   open the `meeting-action-items/` folder. Paths below are relative to that folder.
2. Start a fresh chat. Turn off browsing, tools, and memory/custom instructions
   where possible. Record anything you cannot disable in `results/TEMPLATE.md`.
3. Paste `model/prompt.md`, followed by the complete `model/transcript.md`, as
   **one message**. Use pasted text rather than attachments for this baseline.
   Do not send anything under `evaluator/` or the results template.
4. Create a run folder under `results/` (for example, `results/run-001/`) and save
   the complete response there as `initial.md`. Score it using
   `evaluator/scorecard.md`. Each check is worth one point; no partial credit.
5. If any checks fail, assemble the prescribed feedback from
   `evaluator/feedback.md`. Send it in the same chat and save the revision.
6. Rescore all checks, including previously passed ones. Allow at most two
   correction messages. Stop early if all 10 checks pass.
7. Copy `results/TEMPLATE.md` into that run folder and complete it. Keep the
   initial response, revisions, and exact feedback with the record.

No account, script, or Git knowledge is required to score this experiment.

## Consistency rules

- Score the latest response as a complete replacement, not a cumulative answer.
- Do not add hints, answer-key values, or custom explanations to feedback.
- A clarification question or truncated answer is an attempt: score the content
  actually returned and use the regular feedback process. Do not answer the
  clarification separately or request an extra continuation.
- A provider failure with no model response is an infrastructure failure. Retry
  the exact message once and record it; if it fails again, mark the run incomplete.
  A visible refusal or unusable model answer is a scored attempt, not a retry.
- Never edit a response before scoring. Ignore harmless Markdown rendering
  differences only as explicitly allowed by the scorecard.
- Report initial and assisted scores separately. Unused rounds are N/A, not zero.
- Record app/model configuration. Runs with different enabled capabilities are
  different setup groups. One run is an observation, not a stable model ranking.

## Evaluator materials

`evaluator/scorecard.md` includes the answer key and a worked scoring example.
These materials are public but must be withheld from the model during a run.
All people, organizations, and events in the sample are fictional.

Score-affecting changes require a new experiment version. Record both this version
and the Git commit (or `uncommitted` while working locally) in each result.
