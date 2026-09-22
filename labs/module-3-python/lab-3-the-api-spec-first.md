# Lab 3 &mdash; The API, spec-first

**Mission 3 &middot; API** &nbsp;|&nbsp; ~35 minutes &nbsp;|&nbsp; Copilot: **agent mode (builder)**

## The situation

The core works. Now it needs a contract other teams can call. The spec is written, the acceptance tests
are written, and the house rules for this repository are in `.github/copilot-instructions.md`. This is
the setting in which agent mode is at its best, **and** the one in which it is most tempting to stop
reading what it does.

## Read first (5 minutes)

- `docs/api-spec.md` in your AskOps clone, down to the Mission 5 line
- `.github/copilot-instructions.md` &mdash; the rules the agent will be given
- `askops/deps.py` and `askops/sources.py` &mdash; both complete. Why is `get_store` a function and not a variable?

## Do

1. Commit, so you can see exactly what the agent changes: `git add -A && git commit -m "before mission 3"`.
2. Open Copilot Chat in **Agent** mode, start a new chat, and paste:

   ```text
   Implement docs/api-spec.md up to (not including) the Mission 5 section.
   Write askops/schemas.py first and show it to me before writing askops/api.py.
   The acceptance tests are tests/test_m3_api.py. Do not modify any test.
   When you are done, run: python score.py 3
   ```

3. **Review `schemas.py` before letting it continue.** Check against the spec:

   | Check | OK? |
   |---|---|
   | pydantic **v2** only: `Field`, `ConfigDict`, `model_validate` (not `class Config`, `orm_mode`, `parse_obj`) | |
   | `title` bounded 5..120, `severity` typed as the `Severity` enum | |
   | `IncidentOut` can be built from the dataclass (`from_attributes=True`) | |

4. Let it write `api.py` and run the tests. Approve terminal commands one at a time.
5. Review `api.py` yourself, line by line, before you commit. In particular:
   - Is `/ask` `async def`, and does it `await asyncio.gather(...)` the two sources?
   - Is every `RunbookNotFound` turned into a 404 **in `api.py`**, not in the store?
   - Any `except Exception`? Any `print`? Any module-level store?
6. Run it for real:

   ```bash
   uvicorn askops.app:app --reload
   ```

   Open <http://127.0.0.1:8000/docs>. Try `POST /api/incidents` with a 3-character title and read the
   422 body. You did not write that validation message. pydantic did, from one `Field(min_length=5)`.

## Notice

- **`async def` is not "faster".** It lets the event loop run *other* work while this request waits on
  I/O. Two awaits in a row still wait twice. `asyncio.gather` is what makes them overlap, and
  `test_ask_consults_both_sources_concurrently` measures it.
- **The opposite trap:** a blocking call (`time.sleep`, `requests.get`, a synchronous DB driver) inside
  `async def` freezes *every* request on that worker. A plain `def` endpoint is safer for blocking code,
  because FastAPI runs it in a thread pool.
- **Dataclass for the domain, pydantic for the wire.** They look redundant today. They change for different
  reasons: the day the API needs a v2 field, the domain should not care.

## Done when

`python score.py 3` shows **Score: 11/11**, missions 1 and 2 are still green, and `/docs` loads. Commit
with a message that says *why*, not just *what*.

## Stretch

Add `GET /api/incidents?severity=high`, test first: ask the agent to write **only the test** and stop. Review
the test, run it red, then ask for the implementation.
