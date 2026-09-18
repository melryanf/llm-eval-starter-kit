# Scorecard and answer key — 1.0.0

Withhold this file from the model. Score each check independently as 0 or 1.
Read action content even if the model uses prose instead of a table: formatting
is scored separately by FMT-01. An omitted action fails its corresponding check.
Duplicated or extra actions fail ACT-06, not otherwise-correct action checks.

Accept equivalent wording (e.g. “verify booking” for “confirm room booking”),
capitalization, whitespace, and Markdown emphasis. Owner full names and date
values must match. Dates must use YYYY-MM-DD; a correct date written differently
fails its action check. `Unassigned` and `Not specified` are case-insensitive but
must be those phrases. An explicit conflicting value fails the affected check,
even if the correct value also appears elsewhere.

| ID | Pass condition | Exact failure message |
|---|---|---|
| ACT-01 | Room booking confirmation assigned to Noah Brooks, deadline 2026-04-08. | The room-confirmation action is missing or has an incorrect owner or deadline. |
| ACT-02 | Invitation sending assigned to Priya Shah, deadline 2026-04-10. | The invitation action is missing or has an incorrect owner or deadline. |
| ACT-03 | Budget revision to fit the $600 cap assigned to Leo Ortiz, deadline 2026-04-08. | The budget-revision action is missing or has an incorrect scope, owner, or deadline. |
| ACT-04 | Venue portable hearing-loop check, owner Unassigned, deadline 2026-04-09. | The hearing-loop action is missing or has an incorrect owner or deadline. |
| ACT-05 | Attendee feedback-form draft assigned to Priya Shah, deadline Not specified. | The feedback-form action is missing or has an incorrect owner or deadline. |
| ACT-06 | No extra, completed, withdrawn, or duplicate actions. Missing actions alone do not fail this check. | The answer includes an extra, completed, withdrawn, or duplicate action. |
| DEC-01 | Decisions include Library Room, workshop date 2026-04-25, and a $600 total event spending cap. The decision date may also be written April 25, 2026. | The venue, event date, or total spending-cap decision is missing or incorrect. |
| DEC-02 | Decisions include free attendance AND required advance registration. | The attendance or registration decision is missing or incorrect. |
| DEC-03 | Decisions include no livestream for this workshop AND digital-only promotion; no invented or contradictory decisions. | The livestream or promotion decision is missing or incorrect, or an unsupported decision was added. |
| FMT-01 | Exactly Actions and Decisions sections; Actions is a Markdown table with exactly Action, Owner, Deadline columns; Decisions is a bulleted list; no other prose. Heading depth and optional outer table pipes do not matter. Empty sections fail. | Use exactly the requested Actions table and Decisions bullet list, with the prescribed columns and no extra sections or commentary. |

## Full-credit example

## Actions

| Action | Owner | Deadline |
|---|---|---|
| Confirm the Library Room booking | Noah Brooks | 2026-04-08 |
| Send the invitation | Priya Shah | 2026-04-10 |
| Revise the budget to fit the $600 cap | Leo Ortiz | 2026-04-08 |
| Check whether the venue has a portable hearing loop | Unassigned | 2026-04-09 |
| Draft an attendee feedback form | Priya Shah | Not specified |

## Decisions

- Hold the workshop in the Library Room on April 25, 2026.
- Cap total event spending at $600.
- Attendance is free, with advance registration required.
- Do not livestream this workshop.
- Use digital-only promotion.

## Scoring calibration

The example above scores 10/10. If it is changed to assign the hearing-loop check
to Noah Brooks, use April 9 for the invitation deadline, and add poster printing
as a sixth action, it scores 7/10: ACT-02, ACT-04, and ACT-06 fail. Other checks
still pass. This illustrates scoring requirements independently.

If a response says only “What format do you want?”, ACT-06 passes because there
are no extra actions; all other checks fail. Score 1/10, fully passed: no.
A partial score is not equivalent to a useful or completed answer.
