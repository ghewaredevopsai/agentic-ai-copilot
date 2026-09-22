# Mission 4 &mdash; the web page, solved with Copilot

**Lab:** [Lab 4 &mdash; Put a web page on it](../lab-4-put-a-web-page-on-it.md) &nbsp;|&nbsp; **Checks:** 8 &nbsp;|&nbsp;
**Copilot:** Agent mode &nbsp;|&nbsp; **Code:** [`code/mission-4/`](code/mission-4/)

## Before you start

- Missions 1 to 3 are green, or you are on the `mission-4-start` tag.
- `git add -A && git commit -m "before mission 4"`
- Agent mode, new chat.

## 1. Build the page

```text
Implement docs/web-spec.md in askops/web.py and new templates under askops/templates/.
- Full page index.html extends base.html. Fragments for htmx do not extend anything:
  one for the ask results, one for an incident table row, one for an error row.
- Render every template with templates.TemplateResponse(request, name, context). Never build HTML with
  f-strings or string concatenation.
- /ui/ask reuses sources.runbook_hits and sources.incident_hits with asyncio.gather, and shows each runbook's
  steps as an ordered list.
- POST /ui/incidents reads Form fields and validates with IncidentIn from askops/schemas.py. On
  ValidationError return the error row with status 200 and create nothing.
Do not modify tests or base.html. Finish by running python score.py 4 and fix anything red.
```

**Check, in `git diff`:**
- four templates: `index.html`, a results fragment, an incident row, an error row
- `hx-get="/ui/ask" hx-target="#results"` on the ask form; `hx-post` with `hx-swap="afterbegin"` on the incident form
- no `f"<` anywhere in `web.py`, and no `|safe` in any template
- validation goes through `IncidentIn`, not a second set of hand-written checks

## 2. Use it

```bash
uvicorn askops.app:app --reload
```

Open <http://127.0.0.1:8000>. Ask *deploy rollback*. Open an incident. Open one titled `no`. In the browser's
network tab, confirm the responses are HTML fragments and the page never reloads.

## 3. Explain it back

Ask mode:

```text
In my templates, what stops a search for <script>alert(1)</script> from running in the browser?
Show me the one change that would make it vulnerable, without applying it.
```

## Done

```bash
python score.py 4        # Score: 8/8
python score.py 1 2 3    # still green
git add -A && git commit -m "Mission 4: AskOps web page with htmx, no page reloads"
```

## Stretch

```text
The error row stays in the table after a later successful submit. Show the validation error in a
<p id="form-error"> above the form instead, using the HX-Retarget and HX-Reswap response headers.
Do not modify tests. Run python score.py 4.
```
