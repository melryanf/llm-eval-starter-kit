# Correction feedback — 1.0.0

Send the following message with placeholders replaced. Include only failed check
IDs and their **exact** failure messages from the scorecard, sorted by ID. Do not
include pass conditions or the reference answer. Report all failures, even if a
check failed previously. Round is 1 or 2. Do not send feedback after a full pass.

```text
Experiment: meeting-action-items
Version: 1.0.0
Feedback round: {round} of 2

Failed checks:
- {ID}: {exact failure message}

Return the entire revised answer addressing these failures. Preserve all
requirements that already passed. The original task and inputs are unchanged.
```
