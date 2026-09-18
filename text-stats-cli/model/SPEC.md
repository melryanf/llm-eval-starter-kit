# Text statistics CLI — specification 1.0.0

Create `text_stats.py`, a command-line program invoked as:

```text
python3 text_stats.py [FILE]
```

## Inputs and interface

- With no argument, read all input bytes from standard input until EOF.
- With the single argument `-`, also read standard input.
- Any other single argument is a file path, including paths containing spaces.
  Read the file, ignoring standard input. There are no flags or options, including
  no special `--help` behavior. A path beginning with `-` is still a path unless
  it is exactly `-`.
- More than one argument is a usage error. Detect this before reading any input.
- Decode bytes as strict UTF-8, without BOM removal or newline translation.
  An initial UTF-8 BOM therefore becomes one U+FEFF character.
- Empty input is valid. Inputs used in this experiment are small enough to fit
  into memory. Assume standard output and standard error are writable.

## Output

On success, exit 0 and write exactly one JSON object followed by one LF (`\n`)
to standard output. Write nothing to standard error. No whitespace may appear
outside the JSON object except that final LF. JSON object spacing and key order
are unrestricted. Include exactly these keys with nonnegative integer values
(not booleans):

- `characters`: number of Unicode code points in the decoded text, including
  whitespace and line endings. Do not count UTF-8 bytes or visual graphemes.
- `words`: number of nonempty runs separated by Unicode whitespace, specifically
  the behavior of Python `str.split()` with no arguments. Punctuation stays
  within a word.
- `lines`: 0 for empty text. Otherwise count LF characters (`\n`), plus 1 if
  the text does not end with LF. CR (`\r`) and Unicode line separators do not
  create lines for this count.

For example, input bytes representing `Hello world\n` produce values
`characters=12`, `words=2`, `lines=1`.

## Errors

For unreadable files (including missing paths and directories), invalid UTF-8,
or too many arguments: exit 2, write no standard output, and write exactly one
nonempty line to standard error, starting with `error:` and ending with LF.
The message after the prefix must contain non-whitespace text. Do not print a
traceback. The exact message is otherwise unrestricted.

Output must be deterministic for identical input and arguments. Do not modify
input files, read unrelated files, access the network, or start other programs.
