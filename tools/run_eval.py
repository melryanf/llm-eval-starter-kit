#!/usr/bin/env python3
"""Run a pilot experiment against models through the opencode CLI.

Each (model, repeat) gets a fresh session and a run folder under
<experiment>/results/. text-stats-cli is scored with evaluator/check.py and
gets up to two correction rounds; meeting-action-items saves the initial
response for manual scoring. Generated code executes on this machine: use a
disposable environment.
"""

import argparse
import datetime
import json
import os
import platform
import re
import shutil
import signal
import subprocess
import sys
import tempfile
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OPENCODE_CONFIG = ROOT / "tools" / "opencode.jsonc"
INPUTS = {
    "text-stats-cli": ("model/prompt.md", "model/SPEC.md"),
    "meeting-action-items": ("model/prompt.md", "model/transcript.md"),
}
PYTHON_TAGS = {"python", "py", "python3"}


def parse_events(out, err, returncode):
    """Turn `opencode run --format json` output into one reply dict."""
    text, session, error = [], None, None
    tokens, cost = dict.fromkeys(("input", "output", "reasoning"), 0), 0.0
    for line in out.splitlines():
        try:
            event = json.loads(line)
        except ValueError:
            continue
        session = event.get("sessionID", session)
        if event.get("type") == "error":
            error = json.dumps(event.get("error"))[:300]
            continue
        part = event.get("part", {})
        if part.get("type") == "text":
            text.append(part.get("text", ""))
        elif part.get("type") == "step-finish":
            for key in tokens:
                tokens[key] += part.get("tokens", {}).get(key, 0)
            cost += part.get("cost", 0)
    if not error and returncode:
        error = f"opencode exited {returncode}: {err.strip()[-200:]}"
    if not error and not "".join(text).strip():
        error = "empty response"
    return {"text": "".join(text), "session": session, "tokens": tokens, "cost": cost, "error": error}


def ask_opencode(model, message, session, scratch, timeout):
    # stdin must be closed: `opencode run` blocks waiting on it otherwise.
    cmd = ["opencode", "run", "-m", model, "--agent", "eval", "--format", "json", "--pure"]
    if session:
        cmd += ["-s", session]
    env = {**os.environ, "OPENCODE_CONFIG": str(OPENCODE_CONFIG)}
    proc = subprocess.Popen(cmd + [message], cwd=scratch, env=env, stdin=subprocess.DEVNULL,
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
                            start_new_session=True)
    try:
        out, err = proc.communicate(timeout=timeout)
    except subprocess.TimeoutExpired:
        os.killpg(proc.pid, signal.SIGKILL)
        proc.communicate()
        return {"text": "", "session": session, "tokens": {}, "cost": 0.0,
                "error": f"timeout after {timeout}s"}
    return parse_events(out, err, proc.returncode)


def ask_stub(command, message, round_number):
    """Test double: the stub reads the message on stdin and prints the reply."""
    proc = subprocess.run(command, shell=True, input=message, capture_output=True, text=True,
                          env={**os.environ, "EVAL_ROUND": str(round_number)})
    return {"text": proc.stdout, "session": None, "tokens": {}, "cost": 0.0,
            "error": None if proc.returncode == 0 and proc.stdout.strip() else f"stub failed: {proc.stderr[-200:]}"}


def extract_python(response):
    """README rule: exactly one Python block, else an empty (failing) file."""
    blocks = re.findall(r"```([\w+-]*)[^\n]*\n(.*?)```", response, re.DOTALL)
    candidates = [code for tag, code in blocks if tag.lower() in PYTHON_TAGS]
    candidates = candidates or [code for tag, code in blocks if not tag]
    if len(candidates) == 1:
        return candidates[0], "ok"
    return "", f"empty file: {len(candidates)} candidate Python blocks"


def run_checker(experiment, candidate, next_round):
    proc = subprocess.run([sys.executable, str(ROOT / experiment / "evaluator/check.py"),
                           str(candidate), "--round", str(next_round)],
                          capture_output=True, text=True)
    if proc.returncode not in (0, 1):
        sys.exit(f"checker failed to run (exit {proc.returncode}): {proc.stderr}")
    checks = {name: status == "PASS" for name, status in re.findall(r"^(\S+-\d+): (PASS|FAIL)$", proc.stdout, re.M)}
    feedback = re.search(r"BEGIN FEEDBACK\n(.*?)\nEND FEEDBACK", proc.stdout, re.DOTALL)
    return proc.stdout, checks, feedback.group(1) + "\n" if feedback else None


def converse(args, model, message, session, scratch, round_number, failures):
    """One model call; a failed call is retried once, identically."""
    for attempt in range(2):
        reply = (ask_stub(args.stub, message, round_number) if args.stub
                 else ask_opencode(model, message, session, scratch, args.timeout))
        if not reply["error"]:
            break
        failures.append(reply["error"])
        print(f"  ! {reply['error']}" + ("  (retrying once)" if attempt == 0 else ""), file=sys.stderr)
        time.sleep(args.pause)
    return reply


def run_one(args, experiment, model, run_dir, message):
    scored = experiment == "text-stats-cli"
    (run_dir / "submission" if scored else run_dir).mkdir(parents=True)
    rounds, failures, session, status = [], [], None, "complete"
    with tempfile.TemporaryDirectory() as scratch:  # empty cwd outside the repo: no AGENTS.md
        for n in range(3):
            label = "initial" if n == 0 else f"revision-{n}"
            start = time.monotonic()
            reply = converse(args, model, message, session, scratch, n, failures)
            seconds = time.monotonic() - start
            if reply["error"]:
                status = "incomplete"
                break
            session = reply["session"]
            (run_dir / f"{label}.md").write_text(reply["text"])
            entry = {"label": label, "seconds": round(seconds, 1), "tokens": reply["tokens"], "cost": reply["cost"]}
            rounds.append(entry)
            if not scored:
                break
            code, entry["extraction"] = extract_python(reply["text"])
            (run_dir / f"candidate-{label}.py").write_text(code)
            shutil.copy(run_dir / f"candidate-{label}.py", run_dir / "submission/text_stats.py")
            output, checks, feedback = run_checker(experiment, run_dir / "submission/text_stats.py", n + 1 if n < 2 else 0)
            (run_dir / f"check-{label}.txt").write_text(output)
            entry.update(checks=checks, score=sum(checks.values()), total=len(checks))
            print(f"  {label}: {entry['score']}/{entry['total']} ({entry['seconds']}s)")
            if feedback is None or n == 2:
                break
            (run_dir / f"feedback-{n + 1}.md").write_text(feedback)
            message = feedback
            time.sleep(args.pause)
    return rounds, failures, status


def per_round(rounds, fn):
    return "; ".join(f"{r['label']} {fn(r)}" for r in rounds) or "N/A"


def summarize_run(experiment, version, model, run_dir, rounds, failures, status):
    scored = experiment == "text-stats-cli"
    last = rounds[-1] if rounds else {}
    passed = bool(scored and last and last["score"] == last["total"])
    if status == "complete" and not scored:
        status = "awaiting manual scoring"
    return {
        "experiment": experiment, "version": version, "model": model, "run": run_dir.name,
        "status": status, "infrastructure_failures": failures,
        "initial_score": rounds[0].get("score") if rounds else None,
        "final_score": last.get("score"), "total": last.get("total"),
        "fully_passed": passed, "correction_rounds": max(len(rounds) - 1, 0) if scored else None,
        "seconds": round(sum(r["seconds"] for r in rounds), 1),
        "tokens": {k: sum(r["tokens"].get(k, 0) for r in rounds) for k in ("input", "output", "reasoning")},
        "cost": round(sum(r["cost"] for r in rounds), 6), "rounds": rounds,
    }


def git_commit(experiment):
    def git(*a):
        return subprocess.run(["git", "-C", str(ROOT), *a], capture_output=True, text=True).stdout.strip()
    commit = git("rev-parse", "--short", "HEAD")
    return commit if not git("status", "--porcelain", "--", experiment) else f"uncommitted (based on {commit})"


def write_record(experiment, run_dir, record, opencode_version):
    text = (ROOT / experiment / "results/TEMPLATE.md").read_text()
    rounds, provider = record["rounds"], record["model"].split("/")[0]
    tps = lambda r: f"{(r['tokens'].get('output', 0) + r['tokens'].get('reasoning', 0)) / r['seconds']:.1f}" if r["seconds"] else "N/A"
    fields = {
        "Git commit": git_commit(experiment),
        "Run ID / date": f"{run_dir.name}, {datetime.datetime.now().astimezone().isoformat(timespec='seconds')}",
        "Tester": "tools/run_eval.py",
        "Model identifier": record["model"],
        "Provider/app": f"opencode {opencode_version} ({provider})",
        "Generation settings": "provider defaults (not set by the runner)",
        "Enabled tools": "opencode agent 'eval': tools denied, system prompt 'You are a helpful assistant.', "
                         "--pure, empty working directory. Its own setup group, not comparable to pasted-chat runs.",
        "Evaluator OS": f"{platform.platform()}, Python {platform.python_version()}",
        "Infrastructure failures": f"{len(record['infrastructure_failures'])}: " + "; ".join(record["infrastructure_failures"])
                                   if record["infrastructure_failures"] else "0",
        "Status": record["status"],
        "Final fully passed": ("yes" if record["fully_passed"] else "no") if record["total"] else "pending manual scoring",
        "Correction rounds used": record["correction_rounds"] if record["correction_rounds"] is not None else "N/A",
        "Time per round": per_round(rounds, lambda r: f"{r['seconds']}s"),
        "Tokens per round": per_round(rounds, lambda r: "/".join(str(r["tokens"].get(k, 0)) for k in ("input", "output", "reasoning"))),
        "Cost": f"${record['cost']}" if record["cost"] else "N/A (free or not reported)",
        "Output tokens per second": per_round(rounds, tps) + " (includes reasoning; wall clock)",
        "Extraction issues": "; ".join(f"{r['label']}: {r['extraction']}" for r in rounds if r.get("extraction", "ok") != "ok") or "none",
        "Evidence": ", ".join(sorted(p.name for p in run_dir.iterdir() if p.is_file() and p.name != "record.md")),
    }
    if provider == "ollama":
        fields["Local"] = "local Ollama server (hardware/quantization not recorded by the runner)"
    lines = []
    for line in text.splitlines():
        key = next((k for k in fields if line.startswith("- " + k)), None)
        if key:
            line = f"- {line[2:].split(':')[0]}: {fields[key]}"
        table = re.match(r"\| (\S+|\*\*Total.*?\*\*) \| \| \| \|$", line)
        if table and rounds and "checks" in rounds[0]:
            name, cells = table.group(1), []
            for i in range(3):
                if i >= len(rounds):
                    cells.append("N/A")
                elif name.startswith("**"):
                    cells.append(str(rounds[i]["score"]))
                else:
                    cells.append(str(int(rounds[i]["checks"].get(name, False))))
            line = f"| {name} | " + " | ".join(cells) + " |"
        lines.append(line)
    (run_dir / "record.md").write_text("\n".join(lines) + "\n")


def next_run_number(results):
    numbers = [int(m.group(1)) for p in results.glob("run-*") if (m := re.match(r"run-(\d+)", p.name))]
    return max(numbers, default=0) + 1


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("experiment", choices=INPUTS)
    parser.add_argument("--model", action="append", default=[], help="provider/model; repeatable")
    parser.add_argument("--models-file", type=Path, help="one provider/model per line; # comments allowed")
    parser.add_argument("--repeats", type=int, default=1, help="fresh runs per model (default 1)")
    parser.add_argument("--timeout", type=int, default=300, help="seconds per model call (default 300)")
    parser.add_argument("--pause", type=float, default=2, help="seconds between calls (default 2)")
    parser.add_argument("--stub", help="test double: shell command, message on stdin, reply on stdout, round in $EVAL_ROUND")
    parser.add_argument("--dry-run", action="store_true", help="print the message and plan without calling anything")
    args = parser.parse_args()
    sys.stdout.reconfigure(line_buffering=True)

    models = list(args.model)
    if args.models_file:
        models += [m.split("#")[0].strip() for m in args.models_file.read_text().splitlines() if m.split("#")[0].strip()]
    if args.stub and not models:
        models = ["stub"]
    if not models:
        parser.error("give --model, --models-file, or --stub")

    experiment_dir = ROOT / args.experiment
    message = "\n\n".join((experiment_dir / f).read_text().strip() for f in INPUTS[args.experiment]) + "\n"
    template = (experiment_dir / "results/TEMPLATE.md").read_text()
    version = re.search(r"^- Version: (\S+)", template, re.M).group(1)
    if args.dry_run:
        print(message)
        print(f"--- {args.experiment} v{version}: {len(models)} model(s) x {args.repeats} run(s): {', '.join(models)}")
        return

    print("WARNING: generated code runs on this machine. Use a disposable environment.", file=sys.stderr)
    opencode_version = "n/a" if args.stub else subprocess.run(["opencode", "--version"], capture_output=True, text=True).stdout.strip()
    results = experiment_dir / "results"
    for model in models:
        for repeat in range(1, args.repeats + 1):
            run_dir = results / f"run-{next_run_number(results):03d}-{re.sub(r'[^A-Za-z0-9.]+', '-', model).strip('-')}"
            print(f"{run_dir.name}  ({model}, repeat {repeat}/{args.repeats})")
            rounds, failures, status = run_one(args, args.experiment, model, run_dir, message)
            record = summarize_run(args.experiment, version, model, run_dir, rounds, failures, status)
            (run_dir / "record.json").write_text(json.dumps(record, indent=2) + "\n")
            write_record(args.experiment, run_dir, record, opencode_version)
            print(f"  -> {record['status']}" + (f", final {record['final_score']}/{record['total']}" if record["total"] else ""))
            time.sleep(args.pause)


if __name__ == "__main__":
    main()
