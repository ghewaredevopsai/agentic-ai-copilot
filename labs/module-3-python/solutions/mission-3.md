# Mission 3 &mdash; the JSON API, solved with Copilot

**Lab:** [Lab 3 &mdash; The API, spec-first](../lab-3-the-api-spec-first.md) &nbsp;|&nbsp; **Checks:** 11 &nbsp;|&nbsp;
**Copilot:** Agent mode &nbsp;|&nbsp; **Code:** [`code/mission-3/`](code/mission-3/)

## Before you start

- Missions 1 and 2 are green, or you are on the `mission-3-start` tag.
- `git add -A && git commit -m "before mission 3"`
- Agent mode, new chat. Leave tool approvals at the default, so you approve each terminal command.

## 1. The contract first, then stop

```text
Read docs/api-spec.md up to (not including) the Mission 5 section, .github/copilot-instructions.md and
tests/test_m3_api.py. Write askops/schemas.py only: RunbookOut (with a classmethod that builds it from a
Runbook, tags sorted), IncidentIn, IncidentOut, HitOut and AskOut, using pydantic v2 APIs only.
Then stop and show me the file. Do not write api.py yet.
```

**Check before you continue:**
- `Field(min_length=5, max_length=120)` on `title`; `severity: Severity`; `service` at least 1 character
- `model_config = ConfigDict(from_attributes=True)` on `IncidentOut` and `HitOut`
- **no** `class Config`, `orm_mode`, `parse_obj` or `.dict()` &mdash; those are pydantic v1

If you see v1 syntax:

```text
That is pydantic v1 syntax. Rewrite schemas.py with pydantic v2 only: ConfigDict, model_validate, Field.
```

## 2. The endpoints

```text
Now write askops/api.py to implement the spec, using the schemas you wrote.
- Every endpoint takes store: Store = Depends(get_store).
- RunbookNotFound becomes HTTPException 404 with detail str(exc), in api.py only.
- /ask is async def and awaits sources.runbook_hits and sources.incident_hits together with asyncio.gather.
- /ask returns 422 if q is shorter than 3 characters or has no word of 3+ characters.
Do not modify tests. Finish by running python score.py 3 and fix anything red.
```

**Check, in `git diff askops/api.py`:**
- `await asyncio.gather(...)`, not two awaits in a row
- `HTTPException` appears only in `api.py`
- no `except Exception`, no `print`, no module-level `Store`
- `status_code=201` on the POST, `response_model=` on each route that returns a model

## 3. Use it

```bash
uvicorn askops.app:app --reload
```

Open <http://127.0.0.1:8000/docs>, send `POST /api/incidents` with a 3-character title, and read the 422.

## 4. Explain it back

Ask mode:

```text
In askops/api.py, what would happen to other requests on this worker if /ask called time.sleep(0.2) twice
instead of awaiting the sources? And what would change if ask were a plain def?
```

## Done

```bash
python score.py 3        # Score: 11/11
python score.py 1 2      # still green
git add -A && git commit -m "Mission 3: AskOps JSON API with pydantic contracts and concurrent /ask"
```

## If a check stays red

`test_ask_consults_both_sources_concurrently` is the one most often red:

```text
test_ask_consults_both_sources_concurrently fails: /ask takes about 0.4s. Explain why, then make the two
source calls run concurrently. Do not modify tests. Run python score.py 3.
```
