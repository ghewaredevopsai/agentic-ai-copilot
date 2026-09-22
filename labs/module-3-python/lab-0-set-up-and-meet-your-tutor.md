# Lab 0 &mdash; Set up, and meet your tutor

**Tier 0 &middot; You already know this** &nbsp;|&nbsp; ~5 minutes

## Do

1. Clone AskOps and install it: [Set up](README.md#set-up).
2. Run the scoreboard. **Almost everything should be red** (the one green check is the bundled htmx file).

   ```bash
   python score.py
   ```

   ```text
   Mission 1 - Python drills
     [FAIL] test_word_counts_is_case_insensitive
            NotImplementedError
   ...
   Score: 1/56
   ```

3. Open Copilot Chat, type `/tutor` and press Enter. When it asks for the task, answer `word_counts`, and
   tell it the language you know best.
4. Watch the order it works in: an explanation against your language, the code, the test run, the one line
   that matters, and a question for you. **Answer the question** before you go on.

## Notice

- **Copilot writes the code in every lab of this module. You never type an implementation by hand.** Your
  job is the part an agent cannot do for you: know what the code does, and decide whether it is right.
- The tutor explains by **contrast with your language**, not from zero. That is the module's whole approach:
  you are not learning to program, you are learning where Python is *different*.
- If `/tutor` does not appear in the chat, check that you opened **your clone** as the workspace root: the
  prompt file lives in `.github/prompts/`.
- `pip install -e ".[dev]"` installed your own package in *editable* mode: `import askops` works from
  anywhere in the venv, and edits take effect without reinstalling. It is the Python counterpart of a
  Maven/Gradle module on the classpath, or an `npm link`.

If `pip install` fails with a proxy or SSL error, you are on a network that blocks PyPI. Tell the
trainer now, not in Lab 3.
