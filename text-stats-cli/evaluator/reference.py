"""Evaluator-only reference answer. Never supply this file to the model."""

import json
from pathlib import Path
import sys


def main():
    args = sys.argv[1:]
    try:
        if len(args) > 1:
            raise ValueError("expected at most one file path")
        raw = sys.stdin.buffer.read() if not args or args == ["-"] else Path(args[0]).read_bytes()
        text = raw.decode("utf-8")
    except (OSError, ValueError) as error:
        # Keep path names and OS diagnostics with embedded newlines on one line.
        message = " ".join(str(error).split()) or "input could not be read"
        print(f"error: {message}", file=sys.stderr)
        return 2

    counts = {
        "characters": len(text),
        "words": len(text.split()),
        "lines": text.count("\n") + int(bool(text) and not text.endswith("\n")),
    }
    print(json.dumps(counts))
    return 0


if __name__ == "__main__":
    sys.exit(main())
