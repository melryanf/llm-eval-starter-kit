"""Exercise the evaluator with a correct program and deliberate defects."""

from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

from check import evaluate


HERE = Path(__file__).resolve().parent


class EvaluatorVerification(unittest.TestCase):
    def test_reference_passes(self):
        self.assertTrue(all(evaluate(HERE / "reference.py").values()))

    def test_defects_are_detected(self):
        source = (HERE / "reference.py").read_text(encoding="utf-8")
        mutations = [
            ('len(text),', 'len(text.encode("utf-8")),', "CLI-03"),
            ('len(text.split())', 'len(text.split(" "))', "CLI-01"),
            ('text.count("\\n") + int(bool(text) and not text.endswith("\\n"))',
             'len(text.splitlines())', "CLI-02"),
            ('int(bool(text) and not text.endswith("\\n"))',
             'int(not text.endswith("\\n"))', "CLI-04"),
            ('Path(args[0]).read_bytes()',
             'Path(args[0]).read_text(encoding="utf-8").encode("utf-8")', "CLI-05"),
            ('not args or args == ["-"]', 'not args', "CLI-06"),
            ('raw.decode("utf-8")', 'raw.decode("utf-8", errors="replace")', "CLI-07"),
            ('len(args) > 1', 'len(args) > 100', "CLI-08"),
            ('len(text),', 'True,', "CLI-01"),
            ('print(json.dumps(counts))', 'print(json.dumps(counts)); print("extra")', "CLI-01"),
        ]
        with tempfile.TemporaryDirectory() as directory:
            candidate = Path(directory) / "mutant.py"
            for original, replacement, check_id in mutations:
                with self.subTest(check=check_id, mutation=replacement):
                    self.assertIn(original, source)
                    candidate.write_text(source.replace(original, replacement), encoding="utf-8")
                    self.assertFalse(evaluate(candidate)[check_id])

    def test_empty_and_crashing_candidates_fail_all(self):
        with tempfile.TemporaryDirectory() as directory:
            candidate = Path(directory) / "candidate.py"
            for source in ("", "raise RuntimeError('broken')", "this is invalid python!"):
                with self.subTest(source=source):
                    candidate.write_text(source, encoding="utf-8")
                    self.assertFalse(any(evaluate(candidate).values()))

    def test_feedback_and_exit_codes(self):
        with tempfile.TemporaryDirectory() as directory:
            candidate = Path(directory) / "empty.py"
            candidate.write_text("", encoding="utf-8")
            result = subprocess.run(
                [sys.executable, str(HERE / "check.py"), str(candidate), "--round", "1"],
                capture_output=True, text=True, check=False,
            )
            self.assertEqual(result.returncode, 1)
            self.assertEqual(result.stderr, "")
            self.assertIn("Score: 0/8", result.stdout)
            self.assertIn("Feedback round: 1 of 2", result.stdout)
            self.assertIn("BEGIN FEEDBACK", result.stdout)
            ids = [line.split(":")[0] for line in result.stdout.splitlines() if line.startswith("- CLI-")]
            self.assertEqual(ids, [f"- CLI-{number:02}" for number in range(1, 9)])
            missing = subprocess.run(
                [sys.executable, str(HERE / "check.py"), str(candidate.with_name("absent.py"))],
                capture_output=True, check=False,
            )
            self.assertEqual(missing.returncode, 2)

    def test_timeouts_fail_checks(self):
        with patch("check.subprocess.run", side_effect=subprocess.TimeoutExpired("candidate", 5)):
            self.assertFalse(any(evaluate(HERE / "reference.py").values()))


if __name__ == "__main__":
    unittest.main(verbosity=2)
