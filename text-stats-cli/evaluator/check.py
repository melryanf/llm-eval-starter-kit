"""Requirement-level CLI evaluation using only unittest and the standard library."""

import argparse
import io
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


MESSAGES = {
    "CLI-01": "Standard-input processing or the successful JSON output contract failed.",
    "CLI-02": "LF-based line counting failed on newline boundary cases.",
    "CLI-03": "Unicode character or whitespace-based word counting failed.",
    "CLI-04": "Empty-input handling failed.",
    "CLI-05": "File input, literal path handling, or preservation of input bytes failed.",
    "CLI-06": "The explicit '-' standard-input argument failed.",
    "CLI-07": "Unreadable-file or invalid-UTF-8 error handling failed.",
    "CLI-08": "Too-many-arguments error handling failed.",
}


class CandidateChecks(unittest.TestCase):
    candidate = None

    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.cwd = Path(self.directory.name)

    def invoke(self, data=b"", args=()):
        return subprocess.run(
            [sys.executable, str(self.candidate), *args],
            input=data, capture_output=True, cwd=self.cwd, timeout=5,
        )

    def success(self, data, expected, args=()):
        result = self.invoke(data, args)
        self.assertEqual(result.returncode, 0)
        self.assertEqual(result.stderr, b"")
        output = result.stdout.decode("utf-8")
        self.assertTrue(output.startswith("{") and output.endswith("}\n"))

        def unique_object(pairs):
            self.assertEqual(len(pairs), len(dict(pairs)), "Duplicate JSON keys")
            return dict(pairs)

        value = json.loads(output, object_pairs_hook=unique_object)
        self.assertIsInstance(value, dict)
        self.assertEqual(set(value), {"characters", "words", "lines"})
        self.assertTrue(all(type(number) is int and number >= 0 for number in value.values()))
        self.assertEqual(value, dict(zip(("characters", "words", "lines"), expected)))
        # Repeat identical calls to check deterministic output, not just values.
        repeated = self.invoke(data, args)
        self.assertEqual((repeated.returncode, repeated.stdout, repeated.stderr),
                         (result.returncode, result.stdout, result.stderr))

    def error(self, data=b"", args=()):
        result = self.invoke(data, args)
        self.assertEqual(result.returncode, 2)
        self.assertEqual(result.stdout, b"")
        message = result.stderr.decode("utf-8")
        self.assertTrue(message.startswith("error:") and message.endswith("\n"))
        self.assertEqual(message.count("\n"), 1)
        self.assertNotIn("\r", message)
        self.assertTrue(message[len("error:"):-1].strip())

    def test_CLI_01(self):
        self.success(b"Hello world\n", (12, 2, 1))
        self.success(b"one\ttwo  three!", (15, 3, 1))
        self.success(b"one\ttwo", (7, 2, 1))

    def test_CLI_02(self):
        for data, expected in [
            (b"\n", (1, 0, 1)), (b"a\n\n", (3, 1, 2)),
            (b"a\nb", (3, 2, 2)), (b"a\r\nb\r", (5, 2, 2)),
            (b"a\rb", (3, 2, 1)),
        ]:
            with self.subTest(data=data):
                self.success(data, expected)

    def test_CLI_03(self):
        for text, expected in [
            ("café\u00a0猫\t🙂\n", (9, 3, 1)),
            ("e\u0301\u2003x\u2028y", (6, 3, 1)),
            ("\ufeffa", (2, 1, 1)),
            (" \t\r\n", (4, 0, 1)),
        ]:
            with self.subTest(text=text):
                self.success(text.encode("utf-8"), expected)

    def test_CLI_04(self):
        self.success(b"", (0, 0, 0))
        (self.cwd / "empty.txt").write_bytes(b"")
        self.success(b"ignored", (0, 0, 0), ("empty.txt",))

    def test_CLI_05(self):
        for name in ("sample input.txt", "--help"):
            path = self.cwd / name
            data = b"a\r\nb\r"
            path.write_bytes(data)
            self.success(b"ignore this input", (5, 2, 2), (name,))
            self.assertEqual(path.read_bytes(), data)

    def test_CLI_06(self):
        self.success(b"hello\n", (6, 1, 1), ("-",))
        self.success(b"", (0, 0, 0), ("-",))

    def test_CLI_07(self):
        self.error(args=("missing.txt",))
        self.error(args=(str(self.cwd),))
        self.error(data=b"\xff")
        (self.cwd / "invalid.txt").write_bytes(b"\xff")
        self.error(args=("invalid.txt",))

    def test_CLI_08(self):
        (self.cwd / "valid.txt").write_bytes(b"valid input")
        self.error(args=("valid.txt", "extra"))
        self.error(args=("one", "two"))
        self.error(data=b"\xff", args=("-", "extra"))


def evaluate(candidate):
    CandidateChecks.candidate = candidate
    outcomes = {}
    for check_id in MESSAGES:
        suite = unittest.TestSuite([CandidateChecks("test_" + check_id.replace("-", "_"))])
        result = unittest.TextTestRunner(stream=io.StringIO()).run(suite)
        outcomes[check_id] = result.wasSuccessful()
    return outcomes


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("candidate", type=Path)
    parser.add_argument("--round", type=int, choices=(0, 1, 2), default=0,
                        help="next feedback round; 0 prints scores only")
    args = parser.parse_args()
    candidate = args.candidate.resolve()
    if not candidate.is_file():
        parser.error("candidate must be an existing Python file")
    outcomes = evaluate(candidate)
    print("Experiment: text-stats-cli | Version: 1.0.0")
    for check_id, passed in outcomes.items():
        print(f"{check_id}: {'PASS' if passed else 'FAIL'}")
    score = sum(outcomes.values())
    print(f"Score: {score}/{len(outcomes)}")
    if score != len(outcomes) and args.round:
        print("\nBEGIN FEEDBACK")
        print("Experiment: text-stats-cli\nVersion: 1.0.0")
        print(f"Feedback round: {args.round} of 2\n\nFailed checks:")
        for check_id, passed in outcomes.items():
            if not passed:
                print(f"- {check_id}: {MESSAGES[check_id]}")
        print("\nReturn the entire replacement text_stats.py in one Python code block.")
        print("Address these failures and preserve all requirements that already passed.")
        print("The original task and inputs are unchanged.")
        print("END FEEDBACK")
    return int(score != len(outcomes))


if __name__ == "__main__":
    sys.exit(main())
