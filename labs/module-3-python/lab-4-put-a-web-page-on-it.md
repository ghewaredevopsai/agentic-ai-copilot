# Lab 4 &mdash; Put a web page on it

**Mission 4 &middot; Web page** &nbsp;|&nbsp; ~20 minutes &nbsp;|&nbsp; Copilot: **agent mode (builder)**

## The situation

The on-call engineers do not want `curl`. They want a page: ask a question, see the runbook steps, open
an incident, all without a page reload. And nobody on the team wants to maintain a JavaScript build for it.

The answer is server-rendered HTML with **htmx**: attributes like `hx-get` make any element fetch an
HTML fragment from your server and swap it into the page. The server stays in Python. htmx is already
vendored in `askops/static/`.

## Read first (3 minutes)

- `docs/web-spec.md` in your AskOps clone
- `askops/templates/base.html` &mdash; the layout and all the CSS; you should not need to write any style

## Do

1. Commit. Then, in **Agent** mode, new chat:

   ```text
   Implement docs/web-spec.md in askops/web.py and new templates under askops/templates/.
   Extend base.html. Reuse IncidentIn from askops/schemas.py for validation and the functions in
   askops/sources.py for search. Do not modify tests. Finish by running: python score.py 4
   ```

2. While it works, predict: **how many new HTML files** will a clean solution need, and why a fragment
   template and not an f-string?
3. Review the diff. Check especially that no HTML is built with f-strings or string concatenation.
4. Run it and use it:

   ```bash
   uvicorn askops.app:app --reload
   ```

   Open <http://127.0.0.1:8000>. Ask *deploy rollback*. Open an incident. Open one with the title `no`.
   Open the browser's network tab and watch what comes back: HTML fragments, not JSON.

## Notice

- **One contract, two front ends.** The form posts field by field, the API posts JSON, and both are
  validated by the same `IncidentIn`. If the agent wrote a second set of checks in `web.py`, reject it.
- **`test_ui_ask_escapes_the_query`** sends `<script>` as the query. Jinja2 escapes it because the template
  ends in `.html`. The same line written as an f-string is a stored-XSS finding in your next pen test.
- **Status 200 for a validation error** looks wrong to an API designer, and it is deliberate. htmx does not
  swap error responses into the page by default. Know the rule before you "fix" it in review.

## Done when

`python score.py 4` shows **Score: 8/8**, and you have used the page in a browser. **You have built a
Python web app.** Commit.

## Stretch

The error row stays in the table after a successful submit. Fix it: return the error into a
`<p id="form-error">` using the `HX-Retarget` response header instead.
