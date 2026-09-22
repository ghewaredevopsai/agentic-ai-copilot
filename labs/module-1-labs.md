# Module 1 labs — Prompt and context engineering

**Day 1** · Labs 1, 2, 3 and 4 (+ one stretch) · about 105 minutes · Repository:
`global-bank-account`

These four labs are about one thing: the request you send to the agent, and what you can check
afterwards.

- **Lab 1** asks the same ticket twice, once the ordinary way and once in six parts.
- **Lab 2** asks for the answer in a fixed shape, so a script can check it.
- **Lab 3** writes the rules down in the file Copilot reads on every request.
- **Lab 4** measures whether any of it helped, on three real tickets.

## Words used in these labs

- **Instruction file:** a file of facts about this repository. Copilot reads it on every request.
  It lives at `.github/copilot-instructions.md`.
- **Skill file:** a file of steps for one kind of task. Copilot loads it by itself when your task
  matches the skill's description. It lives at `.github/skills/<name>/SKILL.md`.
- **Prompt file:** a saved prompt that you run by typing `/` and its name. It lives in
  `.github/prompts/`. It can take inputs, such as a ticket number.
- **Stop condition:** a named situation where the agent must stop and ask you, instead of guessing.
- **Eval set:** short for evaluation set. A small, fixed set of tickets you use to test a prompt.

## Before you start

Do the one-time setup in [README.md](README.md) first. You need the clone, the tags, and one VS Code
window holding both `global-bank-account` and this course folder.

Check that your clone is clean before you start:

```bash
cd ~/gb-labs/global-bank-account
git status --short
# must print nothing. If it lists files, stash them: git stash push -u -m "before module 1"
```

Your notes go in `labs/my-work/` in this course folder. That folder is yours. You do not commit it.

---

## Lab 1 — The prompt teardown

**Goal:** see what an ordinary request leaves the agent to guess, and what the six-part request
changes · **Ticket:** GB-151 · **Timebox:** 20 min · **Output:**
`labs/my-work/lab-1-teardown.md` — two file counts and your list of fix-up prompts

Slides 4 and 5 showed six parts of a good request: **goal, constraints, inputs, output contract,
done criteria and stop conditions**. In this lab you run both versions and count the difference.
Keep slide 5 open while you work.

You are not trying to finish GB-151. You are watching how the agent looks for its facts.

### Step 1 — Branch (2 min)

```bash
cd ~/gb-labs/global-bank-account
git switch -c lab-1-teardown m3-start
ls docs/adr
# must list four ADRs and a README
```

### Step 2 — The ordinary request (7 min)

**Prompt 1-A** · Agent mode · base model · **new chat**

```text
Add a reversal endpoint for postings.
```

That is the whole prompt. It is what most people type.

While it works:

- **Watch the tool calls.** Copilot lists every file it reads. Keep a count of the different files.
- Each time it does something you would correct in a review, **type a correction and write your
  correction down**. Those are your fix-up prompts, and Step 4 uses them.
- Stop it after **five minutes**, with the **Stop** button, whether or not it has finished.

**What you should see:** Copilot searches the repository before it writes anything. It opens the
posting classes, and usually several files it does not need. It then makes decisions the ticket
already answers, such as whether a reversal deletes the posting.

Write two things in `labs/my-work/lab-1-teardown.md`: the number of different files it opened, and
every fix-up prompt you typed.

Then put the repository back:

```bash
git stash push -u -m "lab 1 run A"
git status --short
# must print nothing
```

"No local changes to save" is fine. It means the run changed nothing.

### Step 3 — The same ticket, in six parts (8 min)

**Prompt 1-B** · Agent mode · base model · **new chat**

First type `#file:GB-151.md` and pick `labs/tickets/GB-151.md` from the list. Then paste the rest.

```text
Read the ticket #file:GB-151.md

GOAL
Add POST /api/v1/postings/{postingId}/reversal.

CONSTRAINTS
- Follow docs/conventions.md and .github/instructions/api.instructions.md.
- A reversal is a status change on the original posting. It never deletes it (docs/glossary.md).
- Balances are derived from ledger entries. Never store a balance.

INPUTS
- src/main/java/in/brainupgrade/accountservice/posting/service/PostingService.java
- src/main/java/in/brainupgrade/accountservice/posting/domain/Posting.java
- The ticket, all six acceptance criteria
- Copy the style of src/main/java/in/brainupgrade/accountservice/posting/api/PostingController.java

OUTPUT CONTRACT
- A service method, a controller method and slice tests. No new dependencies.
- Errors as ProblemDetail, through the existing ApiExceptionHandler.

DONE
- mvn test passes, and the new test fails against the code as it is now.
- Reversing a posting that is already reversed is rejected.

STOP
- If no file in this repository says how a reversal is recorded, stop and ask. Do not choose.
- Do not change any existing ledger entry.
```

Count the different files again, the same way. Stop it after five minutes.

**What you should see:** Copilot opens the named files first and searches far less. Its first answer
quotes a rule and names the file it came from. Both runs may end unfinished, and that is fine. The
number you care about is the file count.

Put the repository back again:

```bash
git stash push -u -m "lab 1 run B"
git status --short
# must print nothing
```

### Step 4 — Turn your fix-ups into stop conditions (3 min)

Read your list of fix-up prompts. Each one is a rule you had in your head and the agent did not
have. Write each one again as a situation the agent can check.

| Your fix-up prompt | As a stop condition |
|---|---|
| "No, do not delete the posting" | "If the ticket does not say how a record is removed, stop and ask." |
| "Use a slice test, not @SpringBootTest" | (this is a fact, not a stop condition — it belongs in the instruction file) |
| (yours) | (yours) |

"Ask if you are unsure" changes nothing. The model does not feel unsure the way a person does. A
stop condition must name something the agent can check, such as "if no ADR covers this design
choice".

Keep this file. Lab 3 and Lab 4 both use it.

### If you are behind

Do Step 2 only, and bring your file count and your fix-up prompts to the debrief. Read Prompt 1-B
without running it.

---

## Lab 2 — The output contract

**Goal:** ask for an answer in a shape a script can check, then check it · **Ticket:** GB-151 ·
**Timebox:** 15 min · **Output:** `~/gb-labs/lab-2-contract.json` — valid JSON, and every source a
file that really exists

Slide 7 showed the shape. This lab writes it, validates it, and then breaks it on purpose.

### Step 1 — Branch (1 min)

```bash
cd ~/gb-labs/global-bank-account
git switch -c lab-2-contract m3-start
```

### Step 2 — Ask for the object (6 min)

**Prompt 2-A** · Agent mode · base model · **new chat**

```text
Read the ticket #file:GB-151.md
Do not change any file. Plan the change only.
Reply with this JSON object and nothing else. No sentence before it, and no text after it.
{
  "ticket": "GB-151",
  "files_changed": ["repository-relative path of each file you would change or add"],
  "rules_used": [{ "rule": "the rule in your own words",
                   "source": "the repository file the rule came from" }],
  "tests_added": ["the test class and method name for each test you would add"],
  "unresolved": ["anything this repository does not answer"]
}
Every "source" must be a path that exists in this repository, with its full file name.
If you cannot find a file for a rule, leave the rule out and put it under "unresolved" instead.
```

**What you should see:** one JSON object, with three or four rules, each naming a real file such as
`.github/copilot-instructions.md` or `docs/adr/ADR-003-amounts-as-minor-units.md`. `files_changed`
should hold the service, the controller and a test file, because the contract on slide 5 asks for
all three.

Copy the reply into a new file, `~/gb-labs/lab-2-contract.json`. Save it next to your clone, so the
checks below can resolve the paths inside it.

### Step 3 — Check it (4 min)

```bash
cd ~/gb-labs/global-bank-account
python -m json.tool ~/gb-labs/lab-2-contract.json > /dev/null
# must print nothing. Anything else means the reply was not a JSON object
```

Then check the five fields, and that every source is a real file:

```bash
python - <<'EOF'
import json, os, sys
d = json.load(open(os.path.expanduser("~/gb-labs/lab-2-contract.json")))
missing = [k for k in ("ticket", "files_changed", "rules_used", "tests_added", "unresolved")
           if k not in d]
if missing:
    sys.exit("missing fields: " + ", ".join(missing))
bad = [r["source"] for r in d["rules_used"] if not os.path.exists(r["source"])]
if bad:
    sys.exit("not a file in this repository: " + ", ".join(bad))
EOF
# must print nothing
```

If you have `jq` and prefer it, `jq -e '.ticket and .rules_used' ~/gb-labs/lab-2-contract.json` does
the first half of the same job.

**If a source fails the check,** read it carefully before you fix it. `docs/adr/ADR-003.md` looks
right and is not a file. The real name is `docs/adr/ADR-003-amounts-as-minor-units.md`. A source you
cannot open is not grounding. It is a guess in the shape of a citation.

### Step 4 — Break it on purpose (3 min)

**Prompt 2-B** · Agent mode · base model · **new chat**

Send Prompt 2-A again, with two changes. Delete the two lines about `source` at the end. Then cut
the line that starts `Reply with this JSON object` back to `Reply with this JSON object.` Save the
reply as `~/gb-labs/lab-2-loose.json` and run the first check from Step 3 on it.

**What you should see:** usually a sentence before the object, a code fence around it, or both.
`python -m json.tool` then fails. Sources may lose their file names. This is why the contract says
plainly that the reply is the object and nothing else.

### Step 5 — Record (1 min)

In `labs/my-work/lab-2-contract.md`, write which check failed first in Step 4, and which of the five
fields you would keep on a real ticket in your own team.

```bash
git status --short
# must print nothing
```

### If you are behind

Do Steps 2 and 3. Skip Step 4 and read what it says instead.

---

## Lab 3 — Your instruction file

**Goal:** write the house rules where Copilot reads them, and measure the difference ·
**Timebox:** 30 min · **Output:** your own `.github/copilot-instructions.md`, committed, plus the
before and after table in `labs/my-work/lab-3-rules.md`

This lab starts from `m1-start`, an earlier checkpoint. It holds the posting service and its tests,
and nothing the team knows is written down yet. You write that file yourself. First, though, you
measure what happens without it. Otherwise you will never know whether your file changed anything.

### Step 1 — Branch (2 min)

```bash
cd ~/gb-labs/global-bank-account
git switch -c lab-3-instructions m1-start
ls .github
# must list one entry: workflows
mvn test
# expect: Tests run: 4, Failures: 0, Errors: 0
```

### Step 2 — Measure the baseline (7 min)

**Prompt 3-A** · Agent mode · base model · **new chat**

Paste this exactly. You will paste it again in Step 5.

```text
Add a GET endpoint that returns the total amount posted to an account today, with tests.
```

While it works:

- If it asks to run `mvn test`, **allow** it.
- If it asks to add a dependency, **decline**, and note that it asked.

When it finishes, read the diff and fill in the **Before** column. Copy this table into
`labs/my-work/lab-3-rules.md`.

| Question | Before | After |
|---|---|---|
| Money type in the new code: `long` minor units, `double` or `BigDecimal` | | |
| Did it add a stored total or balance field? | | |
| Test style: `@DataJpaTest` or `@WebMvcTest`, or `@SpringBootTest`? | | |
| How is the new dependency wired: constructor, or `@Autowired` on a field? | | |
| Did it use Lombok? | | |
| Did it run `mvn test` before it said it had finished? | | |

**What to notice.** The code around it is itself a kind of instruction. It may copy the posting
package and get most of this right. It may instead copy the older account code beside it, which uses
`double` and a stored balance. Whatever you got, you now have evidence rather than an opinion.

### Step 3 — Undo the baseline (1 min)

```bash
git stash push -u -m "lab 3 baseline"
git status --short
# must print nothing
```

### Step 4 — Draft with `/init`, then cut (10 min)

In a **new chat**, type:

```text
/init
```

Copilot reads the workspace and drafts always-on instructions. **In recent VS Code versions it
writes `AGENTS.md` at the root of the folder**, not `.github/copilot-instructions.md`. If yours
writes `.github/copilot-instructions.md` directly, skip the move below. The command behind
`/init` is *Generate Agent Instructions*. Either file works. This lab uses
`.github/copilot-instructions.md` so everyone ends with the same file.

**Move the draft into `.github/copilot-instructions.md`, and delete `AGENTS.md`.** Both files are
read on every request, so keeping rules in both means two files to maintain and two to disagree.

Now read the draft hard. A generated draft mostly **describes** the project: which folders exist,
what the service does. Copilot can read all of that for itself. What it cannot know is the house
rules. Cut the draft until every line passes three tests:

1. Would Copilot **get this wrong** without the line?
2. Could a reviewer **check this in a diff**?
3. Is it a **rule**, and not a description of code Copilot can already read?

Aim for **25 lines or fewer**. Make sure these rules are in it, in your own words. Every one of them
is true in this repository, and you can see each one in the code:

- Money is a `long` of minor units. Never `double`, `float` or `BigDecimal`
- Every posting writes exactly two ledger entries, one DEBIT and one CREDIT, equal in amount and
  currency
- Balances are derived from entries, never stored. Do not add a balance column
- Constructor injection only. No field injection, and no `@Autowired` on a field
- No Lombok
- Cross-currency postings are rejected. This service does not convert
- Slice tests only: `@DataJpaTest` with `@Import`, or `@WebMvcTest`. Never `@SpringBootTest`
  (a fact. From `m3-start` on, the team keeps it in `.github/instructions/tests.instructions.md`)
- Do not invent an account id, a currency code, a status value or a limit. Say so and ask

**Check that Copilot has found the file now, not in Step 5.** The name has to be exact:
`.github/copilot-instructions.md`, with hyphens, at the root of your clone. Ask anything in chat,
expand **Used N references** under the reply, and look for the file. **Chat: Configure Instructions**
in the Command Palette lists what Copilot has found. A misnamed file is never reported as an error.
It is simply never read.

Commit it, so the resets later do not remove it:

```bash
git add .github
git commit -m "Write down the house rules for Copilot"
git status --short
# must print nothing
```

### Step 5 — Measure again (7 min)

**Prompt 3-A** · Agent mode · base model · **new chat**

Paste the **same** request from Step 2, word for word. Follow the same two rules: allow the tests,
decline dependencies. Then fill in the **After** column.

Expand **Used N references** under the reply and check that `.github/copilot-instructions.md` is
listed.

```bash
git stash push -u -m "lab 3 after"
git status --short
# must print nothing
```

**What to notice.** Look at the rows that changed, and at the rows that did not. Instructions
**steer**; they do not **enforce**. If a rule matters enough that breaking it must fail, that is the
test suite's job, or a reviewer's.

### Step 6 — Compare with the team's file (3 min)

The team wrote their own version. Read it only now:

```bash
git show m3-start:.github/copilot-instructions.md
```

It points at files under `docs/` that your branch does not have. Those arrive at the `m3-start`
checkpoint. Ignore the paths. Look at **which rules they wrote down and you did not**, and at how
short their file is.

Write that list at the end of `labs/my-work/lab-3-rules.md`, under the heading "Rules I did not
write down". That list is the real output of this lab.

### If you are behind

Do Steps 2, 4 and 5, and skip the rest. If you have no time to write the file at all, take the
team's and measure that instead:

```bash
git checkout m3-start -- .github/copilot-instructions.md
```

Then do Step 5. You measured the team's file, not your own. Say so in your notes.

---

## Lab 4 — The A/B: does the new prompt actually work?

**Goal:** run the same three tickets twice, with and without the team's skill file, and read what
changed · **Tickets:** GB-204, GB-205, GB-206 · **Timebox:** 40 min · **Output:** two pass rates out
of 3, and a side-by-side read, in `labs/my-work/lab-4-eval.md`

You run the same three tickets twice. **Column A** uses an ordinary prompt, the way most people type
it, on a branch that does **not** have the skill file. **Column B** uses `/gb-change` on a branch
that does. That makes six runs.

You produce two things, and the second one matters more:

1. A **pass rate** out of 3 for each column. It is coarse. Three tickets cannot tell you much.
2. A **side-by-side read of the two runs** for each ticket. This is where you see what the skill
   file actually did, whether or not the score moved.

**Why Column A runs on a different branch.** A skill file loads by itself whenever your task matches
its `description`. That description says "posting or balance behaviour", and all three tickets are
exactly that. If the file were on the branch, Column A would load it too, and you would be comparing
the skill file with itself.

### Step 1 — Write the pass criteria first (6 min)

This step has no prompt. You write it yourself.

Copy this table into `labs/my-work/lab-4-eval.md`. Read the three tickets in
[`tickets/`](tickets/). For each one, write what a pass means, from its acceptance criteria.

| Ticket | Pass means (write this before any run) | A | B | Changed? |
|---|---|---|---|---|
| GB-204 | | | | |
| GB-205 | | | | |
| GB-206 | | | | |
| **Pass rate** | | **/3** | **/3** | |

Use the same three rules for every ticket:

- The acceptance criteria are met, and `mvn test` passes.
- No file changed that the ticket did not need.
- A ticket you judge unclear passes **only** if the agent stopped and asked. Guessing is a fail.

The three tickets are not the same kind of problem, and that is deliberate:

- **GB-204** is clear from the ticket alone. It is your control. If it fails in B, the skill file is
  too strict.
- **GB-205** is not answered by the ticket, but it **is** answered by the repository:
  `docs/adr/ADR-007-duplicate-suppression.md` says a duplicate is the same `clientReference` **and**
  the same `valueDate`, and that a different amount under the same key is rejected, not merged.
  Decide now whether your pass criterion is the ticket's acceptance criteria alone, or the rule the
  repository already holds. Write down which you chose.
- **GB-206** is answered nowhere. This is the ticket your stop conditions are for.

**Do not change this column after your first run.** If you decide what a pass means after you see
the output, you will favour the prompt you wrote yourself.

### Step 2 — Set up the two branches (5 min)

Column B gets the team's skill file and prompt file, from the `m4-start-gh` checkpoint:

```bash
cd ~/gb-labs/global-bank-account
git switch -c eval-B m3-start
git checkout m4-start-gh -- .github/skills .github/prompts
ls .github/skills/account-change/SKILL.md
# must list the file
```

The prompt file you just copied reads its ticket from a GitHub issue. You are reading tickets as
Markdown, so change that. Open `.github/prompts/gb-change.prompt.md` and replace the whole paragraph
that starts `Find the GitHub issue` with this one line:

```text
Read the ticket file labs/tickets/${input:ticket}.md in the course folder of this workspace.
```

Leave the rest of the file alone. Then check and commit:

```bash
grep -n "GitHub issue\|MCP tools" .github/prompts/gb-change.prompt.md
# must print nothing
git add .github
git commit -m "Add the team's skill file and prompt file"
git tag -f eval-base-B
```

Now make Column A, which has neither file:

```bash
git switch -c eval-A m3-start
git tag -f eval-base-A
ls .github/skills 2>/dev/null
# must print nothing: column A has no skill file
```

You are now on the Column A branch. After every run you go back to that column's base.

### How every run works

1. Start a **new chat**. Set **Agent** mode and the **base model**.
2. Paste the run's prompt exactly.
3. Read each tool request before you select **Allow**.
4. If Copilot lists the files it found and waits for your OK, send: `Go ahead with those files.`
5. Allow about three minutes per run. At four minutes, select **Stop** and score what is there.
6. **Score it.** Look at what changed, and run the tests:

   ```bash
   git status --short
   git diff
   mvn -q test
   ```

   In quiet mode, no `FAILURE` line means the tests passed. `git diff` does not show new files.
   `git status --short` marks them with `??`. Open those in the editor.

   Also read the agent's last message. Did it stop and ask a question? Write **P** or **F** in your
   table, with a few words on why.
7. **Save the run, then reset.** You compare the runs in Step 5, so save each one under a name you
   can find again:

   ```bash
   git stash push -u -m "lab 4 <run name>"   # for example: lab 4 A5
   git reset --hard eval-base-A              # eval-base-B in column B
   git status --short
   # must print nothing
   ```

   "No local changes to save" is fine. It means the run changed nothing. Write that in your table: a
   run that did nothing is a fail, not a missing row.

Do not use `git clean` or `git stash pop` in this lab. Your runs stay in `git stash list`, newest
first.

### Step 3 — Column A: the ordinary prompt (about 11 min)

```bash
git branch --show-current
# must print: eval-A
```

Run all three, in order. Score and reset after each one.

**Prompt 4-A4** · Agent mode · base model · **new chat**

```text
Read the ticket #file:GB-204.md
Implement it in this repository. Run "mvn test" until it passes.
```

**Prompt 4-A5** · Agent mode · base model · **new chat**

```text
Read the ticket #file:GB-205.md
Implement it in this repository. Run "mvn test" until it passes.
```

**Prompt 4-A6** · Agent mode · base model · **new chat**

```text
Read the ticket #file:GB-206.md
Implement it in this repository. Run "mvn test" until it passes.
```

### Step 4 — Column B: the prompt file and the skill (about 11 min)

```bash
git switch eval-B
git branch --show-current
# must print: eval-B
```

Same three tickets, same order, a new chat each time. Score and reset to `eval-base-B` after each
one.

**Prompt 4-B4** · Agent mode · base model · **new chat**

```text
/gb-change ticket=GB-204 goal="Prove the posting limit with tests"
```

**Prompt 4-B5** · Agent mode · base model · **new chat**

```text
/gb-change ticket=GB-205 goal="Handle the same reference and value date with a different amount"
```

**Prompt 4-B6** · Agent mode · base model · **new chat**

```text
/gb-change ticket=GB-206 goal="Let Operations correct the narrative on a posting"
```

If `gb-change` does not appear when you type `/gb-`, check that the file name ends in `.prompt.md`
and sits in `.github/prompts/` at the root of your clone.

### Step 5 — Read the two runs side by side (7 min)

First add up each column: two pass rates out of 3. Then do the part that pays.

For each ticket, put the two runs on screen together. They are in your stash:

```bash
# Find each run by its message, not by counting. A run that changed nothing leaves no
# entry at all, so the numbers shift.
git stash list | grep "lab 4 A6"    # prints e.g. stash@{3}: On ...: lab 4 A6
git stash list | grep "lab 4 B6"

# use the index each line printed
git stash show -p 'stash@{3}' > /tmp/a6.diff
git stash show -p 'stash@{0}' > /tmp/b6.diff
```

Open both files in the editor, side by side. For each ticket, answer these four questions in
`lab-4-eval.md`:

| Question | Where to look |
|---|---|
| Did either run name the file a rule came from? | the agent's last message |
| Did either run read `docs/adr/` before writing? | the tool calls in the chat |
| Do the tests check the same thing, at the same level? | the two diffs |
| Did either run stop and ask, instead of choosing? | the agent's last message |

A pass rate can only move by whole tickets. These four answers move even when the score does not,
and they are what you take back to your own repository.

Then read the score:

| What you see | What it means |
|---|---|
| GB-206 changed from fail to pass | The stop conditions work. That part transfers to your own repository unchanged. |
| GB-205 changed | The skill file sent the agent to the rule the repository already held. |
| GB-204 passed in A and fails in B | The skill file is too strict. That is why a clear ticket is in the set. |
| Nothing changed, but the diffs differ | The usual result with three tickets. The score is too coarse to see it; your four answers are not. |
| Nothing changed, and the diffs match | The instruction file may already do the job in this repository. That is a real result, not a failed lab. |

Three tickets show a direction, not a trend, and certainly not proof. Say so when you report it.

### Record

Write the two pass rates, the tickets whose result changed, and your four answers per ticket in
`labs/my-work/lab-4-eval.md`. Leave the result as it is, even if B scored lower than A.

### If you are behind

Run GB-205 and GB-206 only, and say your pass rates are out of 2. Do not drop GB-206: it is the
ticket this module is about.

---

## Stretch lab (optional) — Add your own stop condition

**Goal:** put one of your Lab 1 fix-up prompts into the skill file, and see whether it changes the
run. Do this if you finish Lab 4 early.

Open `labs/my-work/lab-1-teardown.md` and pick one stop condition from your Step 4 table. On the
Column B branch, add it to the "Stop and ask" section of the skill file:

```bash
git switch eval-B
# edit .github/skills/account-change/SKILL.md, then:
git add .github && git commit -m "Add my stop condition"
git tag -f eval-base-B
```

Run **Prompt 4-B6** again, score it the same way, and reset. Did the agent stop earlier, later, or
not at all? One ticket proves nothing. It does tell you whether the line you wrote is checkable.

If you want a larger eval set, `tickets/` also holds GB-201, GB-202 and GB-203. They are three more
tickets on the same service. Write their pass criteria before you run them.

---

## What you take away

- Six parts, and each one prevents a different failure.
- A stop condition names a situation the agent can check. "Ask if unsure" does nothing.
- An output contract turns an answer a person must read into an answer a script can check.
- A source you cannot open is a guess in the shape of a citation.
- Facts go in the instruction file. Steps go in the skill file. This ticket goes in the prompt.
- Instructions steer; tests enforce.
- "My prompt is better" is an opinion. A pass rate over a fixed set of tickets is a measurement.

---
*Gheware DevOps & Agentic AI · [devops.gheware.com](https://devops.gheware.com)*
