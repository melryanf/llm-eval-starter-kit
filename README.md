# LLM Eval Starter Kit

Two self-contained pilot experiments for comparing cloud and local model setups.

| Pilot | Audience | Scoring | Start here |
|---|---|---|---|
| Meeting action items | Everyday users | 10 manual, objective checks | [Instructions](meeting-action-items/README.md) |
| Text statistics CLI | Developers | 8 executable Python requirements | [Instructions](text-stats-cli/README.md) |

## Download and start

Download this repository using **Code → Download ZIP**, extract it, and open the
README in the experiment folder you want to try. Or clone it:

```sh
git clone https://github.com/melryanf/llm-eval-starter-kit.git
```

Both experiments are included in this repository. Run each experiment's commands
from its own folder unless instructed otherwise. The meeting task needs only a
chat application; the coding task also needs Python 3.11 or newer.

Save local run records under each experiment's `results/` directory. These are
ignored by Git; the blank templates are included in the download.

## Shared protocol

- Start a fresh chat with the prescribed model-facing materials.
- Score the initial response, then allow up to two standardized correction rounds.
- Keep initial and assisted scores separate; save all responses and feedback.
- Compare the same experiment version under the same permitted capabilities.
- Use each experiment's result template to record the exact setup and evidence.

Evaluator materials are public but must not be included in the model context.
This primer measures task-specific results. A single observation does not establish
a general ranking or reliable difference between models.

## Next validation step

Run each pilot with one cloud setup and one local setup, then ask a second person
to follow the instructions independently. Those live runs require your selected
models/applications; no model performance results are included here.

The Python evaluator can be verified locally without a model:

```sh
python3 text-stats-cli/evaluator/verify.py
python3 text-stats-cli/evaluator/check.py text-stats-cli/evaluator/reference.py
```

## Follow-on experiments

After the pilots validate the format:

1. `record-validator`: JavaScript on Node.js, with `node:test` and `node:assert`.
2. `compare-service-quotes`: objective cost and eligibility comparisons.
3. `document-fact-check`: evidence-based answers across short documents.

The Node.js challenge is part of the next batch; the developer pilot uses Python.
