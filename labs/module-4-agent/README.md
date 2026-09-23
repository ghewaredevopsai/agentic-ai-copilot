# Module 4 labs — Agent foundations and tool use

**Day 1** · Labs 4.1, 4.2 and 4.3 · about 75 minutes · **Day 2** · Lab 4.4 · about 15 minutes

In Module 3 you built AskOps. Its `/api/ask` endpoint runs the same two searches every time. In these
labs AskOps becomes an agent: a model chooses which tool to call next, and your code runs it.

| Lab | What you do | Time | Model |
|---|---|---|---|
| 4.1 | Read a complete agent loop in plain Python, then run it | 12 min | fake model |
| 4.2 | Break the agent five ways, fix each one, count the tokens | 35 min | fake model |
| 4.3 | Run the same tools on the GitHub Copilot SDK, and compare | 25 min | your Copilot seat |
| 4.4 | Day 2: run your fixed agent on a real model | 15 min | sandbox model |

## Words used in these labs

- **Tool call:** the model's request to run one tool with some arguments. Your code decides whether
  to run it.
- **Observation:** the tool's result, sent back to the model as a message.
- **Step:** one round trip to the model. **Step budget:** the most steps one run may take.
- **Fake model:** `fake_llm.py`, a small server that replays a script. It is not an AI. It causes
  each failure on demand, with no network.
- **Copilot SDK:** a Python library that uses your Copilot seat as the agent's model. Copilot runs
  the loop for you.

## Before you start

You need **Python 3.14** (3.11 or newer works), a bash terminal and VS Code with Copilot. Labs 4.1
and 4.2 use only the Python standard library, so there is **nothing to install**. Lab 4.3 also needs
**Node.js 22 or newer** (`node --version`) and access to PyPI.

Open **two terminals** in this folder. Terminal 1 runs the model. Terminal 2 runs the agent.

```bash
cd ~/agentic-ai-copilot/labs/module-4-agent
ls
# must list: README.md  agent.py  agent_sdk.py  askops_data.json  fake_llm.py  solutions
```

Your notes go in `labs/my-work/lab-4-agent.md`. That folder is yours, and you do not commit it.

**Do not open `solutions/` until Lab 4.2 Step 5.** It holds one answer to every fix.

---

## Lab 4.1 — Read the loop, then run it

**Goal:** see every message an agent sends and receives · **Timebox:** 12 min · **Output:** three
answers and three token numbers in your notes

### Step 1 — Read `run()` before you run it (7 min)

`run()` is near the bottom of `agent.py`. It is the loop from the deck's *The loop, in plain Python*
slide.

**Prompt 4-A** · Ask mode · base model · **new chat**

```text
Explain the run() function in labs/module-4-agent/agent.py, line by line.
Then answer:
1. Which line is the "reason" step, which is "act" and which is "observe"?
2. How does the loop know the model has finished?
3. What does the loop send to the model on the second call that it did not send on the first?
Do not change any file.
```

Check each answer against the code. Write your own three answers in your notes.

### Step 2 — Run it on the fake model (5 min)

```bash
python fake_llm.py happy        # Terminal 1
python agent.py                 # Terminal 2
```

**You should see:** three ACTION lines over two steps, then an answer that cites RB-101 and says
INC-9001 is already open. The last line is `[3 steps, ... tokens]`.

Terminal 1 prints one line per call. **The messages and the tokens grow on every call**, because
the agent resends the whole list each time (*The message list is the memory*). Write the three
token numbers in your notes.

---

## Lab 4.2 — Make it fail, fix it, count the tokens

**Goal:** cause common agent failures on purpose, fix each in code, and measure what each fix
saves · **Timebox:** 35 min · **Output:** this table, filled in, in your notes

```text
| Scenario | Before the fix: what happened | Steps | Tokens | After the fix: what happened | Steps | Tokens |
|----------|-------------------------------|-------|--------|------------------------------|-------|--------|
| invented |                               |       |        |                              |       |        |
| badargs  |                               |       |        |                              |       |        |
| loop     |                               |       |        |                              |       |        |
| write    |                               |       |        |                              |       |        |
| budget   |                               |       |        |                              |       |        |
| hidden   |                               |       |        |                              |       |        |
```

**For each scenario:** in Terminal 1 press Ctrl+C, then start `python fake_llm.py <scenario>`. In
Terminal 2 run `python agent.py` and record the result. Fix `agent.py` with Copilot, then run the
**same scenario** again. A crash is a result too: write the error, and "crashed" for steps and tokens.

Review every diff before you keep it.

### Step 1 — The invented tool and the wrong argument (Fix 1, 10 min)

Run the `invented` scenario, then `badargs`.

**You should see:** both crash. `invented` stops with `KeyError: 'open_ticket'`: the model asked for
a tool that does not exist. `badargs` stops with `TypeError: get_runbook() got an unexpected keyword
argument 'id'`: right tool, wrong argument name. The line marked `# no checks yet` trusted both.

**Prompt 4-B** · Agent mode · base model · **new chat**

```text
In labs/module-4-agent/agent.py, the line marked "# no checks yet" runs any tool call the model sends.
Add a function run_tool(name, raw_args). Replace the lines that parse the arguments and run the tool
(from args = json.loads(...) to "# no checks yet") with a call to it. Print the raw arguments in the
ACTION line. run_tool must:
- return "ERROR: no tool called <name>." if the tool does not exist
- return "ERROR: bad arguments for <name>: <reason>" if the arguments are not valid JSON,
  or do not match the function (TypeError)
- otherwise run the tool and return its result
It must never raise. The error text goes back to the model as the observation.
Change only agent.py. Keep the standard library only.
```

Run both scenarios again. **You should see:** no crash. In `invented`, the model answers without the
missing tool. In `badargs`, it calls `get_runbook` again with `runbook_id`, and answers. This is the
*The model asks. Your code decides.* slide: return the error as the observation, and the model
usually corrects itself.

### Step 2 — The loop (Fix 2, 8 min)

Run the `loop` scenario.

**You should see:** `list_incidents` six times, then `Stopped: step budget spent.` The step budget
saved you, but you paid for six calls, each bigger than the last.

**Prompt 4-C** · Agent mode · base model · **same chat**

```text
In run(), stop the loop as soon as the model makes the same tool call twice: the same tool name with
the same arguments string. Return "Stopped: <name> called twice with the same arguments." with the
step number and the tokens used, like the other return lines. Change only agent.py.
```

Run `loop` again. **You should see:** the run stops at step 2, with about a fifth of the tokens.

### Step 3 — The write that nobody approved (Fix 3, 7 min)

Run the `write` scenario.

**You should see:** the agent opens INC-9004 for a problem INC-9001 already covers, and nobody was
asked. This is the *Autonomy is set per tool* slide: a tool that writes needs a person's approval,
enforced in code.

**Prompt 4-D** · Agent mode · base model · **same chat**

```text
In run_tool(), before open_incident runs, show the arguments and ask the person at the terminal
"Approve open_incident <args>? [y/N]". Run the tool only if they type y. Otherwise return
"ERROR: a person refused. Do not open an incident." Change only agent.py.
```

Run `write` twice: type `n` once and `y` once. With `n`, the agent says it did not open an incident.

### Step 4 — The token budget, and the error hidden as empty (Fix 4 and Fix 5, 8 min)

These two need no new scenario.

**Token budget (row `budget`).** The step budget limits steps, not cost. Your "before" is the
`happy` run from Lab 4.1.

**Prompt 4-E** · Agent mode · base model · **same chat**

```text
Add MAX_TOKENS = 8000 next to MAX_STEPS in agent.py. After each step, if the tokens used so far are
above MAX_TOKENS, stop and return "Stopped: token budget spent." with the step and tokens.
Change only agent.py.
```

Set `MAX_TOKENS = 500` and run the `happy` scenario. **You should see:** `Stopped: token budget
spent.` at step 2. Put it back to 8000.

**The error hidden as empty (row `hidden`).** When `SEARCH_DOWN` is set, `search_runbooks()`
pretends the runbook source is down and returns `[]`:

```bash
python -c "import os; os.environ['SEARCH_DOWN']='1'; import agent; print(agent.search_runbooks('502 deploy'))"
# prints: []
```

To the model, `[]` means "no runbook matches", so it tells the engineer there is none. The real
problem is that the source is down. Module 3 had the same bug in `/api/ask`, fixed with a 503. Edit
that line by hand to return `"ERROR: runbook search is unavailable. Try again later."`, then run the
command again. This row has no steps or tokens: write what the function returns before and after.

A real tool would retry first (the *Retry, or send the error back?* slide), and send the error only
when the retries are spent.

### Step 5 — Compare with the solution, and save your agent (2 min)

Open `solutions/agent.py`. Each fix is marked `Fix 1` to `Fix 5`. Yours can differ. What matters:
every scenario now ends with an answer or a clear stop, never a crash.

**Save your fixed `agent.py` now** in a private gist or in your notes file. Lab 4.4 on Day 2 runs in
the sandbox, which cannot see your laptop.

### If you are behind

Do Steps 1 and 2. Then run the other scenarios with `python solutions/agent.py` to see the fixed
behaviour.

---

## Lab 4.3 — The same agent on the Copilot SDK

**Goal:** give the same tools to Copilot's own agent loop, and compare what you write with what it
hides · **Timebox:** 25 min · **Output:** the comparison table in your notes

`agent_sdk.py` imports the tool functions from `agent.py`, so the tools are exactly the same. Only
the loop changes: Copilot runs it. **Every run uses your Copilot allowance**, like a chat in VS Code.

### Step 1 — Set up (8 min)

The SDK needs the **Copilot CLI** and your sign-in. Your trainer confirms on the day that your company
allows the Copilot CLI. If it does not, pair with someone whose machine works, and do Step 3 anyway.

Stop the fake model in Terminal 1 first. Then, in Terminal 2:

```bash
npm install -g @github/copilot     # Windows: winget install GitHub.Copilot
copilot                            # type /login, follow the browser steps, then /exit

python -m venv .venv
source .venv/bin/activate          # Git Bash on Windows: source .venv/Scripts/activate
pip install github-copilot-sdk

export COPILOT_CLI_PATH="$(command -v copilot)"
```

The last line points the SDK at the CLI you installed. **On Windows, skip it**: Git Bash gives a
path like `/c/Users/...` that Windows Python cannot use, and the SDK downloads its own copy instead.

### Step 2 — Run it (7 min)

```bash
python agent_sdk.py
```

**You should see:** ACTION lines for the tools Copilot chose, an answer that cites RB-101, and
`[... model calls, ... tokens]`. The model is `gpt-5-mini` unless your trainer names another
(`export ASKOPS_MODEL=<name>`).

Ask for a write:

```bash
python agent_sdk.py "Disk on the report nodes is at 95 percent and nobody has opened an incident. Open one."
```

The SDK asks you to approve `open_incident`. Type `n`, then run it again and type `y`. The question
comes from `approve()`, in your code, not from Copilot.

Ask for something outside its tools:

```bash
python agent_sdk.py "Run the shell command ls and tell me what it prints."
```

It refuses. `available_tools=ToolSet().add_custom("*")` switched off Copilot's own shell and file
tools, so it can use only your four. That is the *Autonomy is set per tool* slide again.

### Step 3 — Compare the two (10 min)

Let Copilot fill the table from the code. Your job is to check it.

**Prompt 4-F** · Agent mode · base model · **new chat**

```text
Compare two versions of the same agent:
- labs/module-4-agent/solutions/agent.py, a plain Python loop
- labs/module-4-agent/agent_sdk.py, the same tools on the GitHub Copilot SDK
Append the table below to labs/my-work/lab-4-agent.md (create the file if it is missing), under the
heading "## Lab 4.3 — plain loop vs Copilot SDK". Fill every cell except the last row.
Rules for each cell:
- at most 15 words, and cite the line numbers you used, like "(L92-L112)"
- answer only from the code in these two files
- if a file has no code for it, write "not in this file", then say who does it instead
- if the answer depends on how the SDK behaves inside, write "SDK decides"
Leave both cells of the last row empty. Change only labs/my-work/lab-4-agent.md.

| Question                                          | agent.py (plain loop) | agent_sdk.py (Copilot SDK) |
|---------------------------------------------------|-----------------------|----------------------------|
| How many lines are the loop itself?               |                       |                            |
| Where is the step budget?                         |                       |                            |
| Can you print the message list sent to the model? |                       |                            |
| Where does the approval for open_incident live?   |                       |                            |
| How do you count tokens per run?                  |                       |                            |
| What happens if the model invents a tool?         |                       |                            |
| Which one would you debug more easily, and why?   |                       |                            |
```

**Check it:** open two cited line numbers and confirm each cell. Fix any cell that is wrong. Then
fill in the last row yourself: that one is your opinion.

**What to notice:** the SDK saves you writing the loop, but you can no longer see or change each step.
What keeps the agent safe is still your code: which tools exist, which need approval, and the token
count.

### If you are behind

Skip Steps 1 and 2 and watch the trainer's run. Prompt 4-F needs only the code, so do Step 3.

---

## Lab 4.4 — On Day 2: the same agent on a real model

**Goal:** see how a real model's path differs from the fake model's script, and test your fixes on
it · **When:** Day 2, in the browser sandbox · **Timebox:** 15 min · **Output:** a new section in
your notes

The sandbox sets `LAB_LLM_BASE_URL` and `LAB_LLM_MODEL`, and `agent.py` reads them. There is nothing
to configure, and you do **not** start `fake_llm.py`.

### Step 1 — Bring your agent to the sandbox (3 min)

Open a terminal in the sandbox:

```bash
cd ~/work/agentic-ai-copilot/labs/module-4-agent
echo "$LAB_LLM_MODEL"
# must print a model name. If it prints nothing, tell your trainer
```

The `agent.py` here is the untouched starter. Create `my_agent.py` next to it and paste in the fixed
agent you saved at the end of Lab 4.2. If you did not save one, use the solution:

```bash
sed 's/\.parent\.parent/.parent/' solutions/agent.py > my_agent.py   # the data file is one folder up
```

### Step 2 — Run it twice on one question, once on another (5 min)

```bash
python my_agent.py
python my_agent.py
python my_agent.py "Logins are slow this morning. Is there a runbook?"
```

Write down the ACTION lines, steps and tokens of each run.

**You should see:** the two runs of the same question may choose different tools, or a different
order. The fake model followed a script. A real model chooses its path at run time (*One call, or a
loop*). Compare the tokens with your Lab 4.1 numbers.

If your loop check stops a run that looked reasonable, write that down. A real model may list the
incidents again after a change, and that repeat is fine. Real loop checks also look at whether
anything changed in between.

### Step 3 — The error hidden as empty, for real (4 min)

```bash
SEARCH_DOWN=1 python agent.py "Disk on the report nodes is at 95 percent. What do I do?"
SEARCH_DOWN=1 python my_agent.py "Disk on the report nodes is at 95 percent. What do I do?"
```

No open incident links to a runbook for this problem, so search is the only way to find one. With
`[]`, the starter's model usually says no runbook exists. With the error text, your agent should say
search is unavailable. That difference is Fix 5.

### Step 4 — Change one description (3 min)

In `my_agent.py`, in `TOOL_SPECS`, change the description of `get_runbook` to `"Gets data."`. Run the
Step 2 questions again. Does the agent still call the right tools? Put the description back.

This agent is where Day 2 starts. In Lab 5.1 you rebuild it with LangChain and compare the two.

---

## What you take away

- An agent is a loop. The model chooses the next step. Your code runs every tool.
- Every call resends the whole message list, so tokens per call grow at every step.
- Check every tool call before you run it. Send errors back as observations. Never crash.
- A loop needs four stop conditions: an answer, a step budget, a loop check, and a clear error the
  model can hand over with. Add a token budget too.
- A tool that writes needs a person's approval, enforced in code.
- A framework or an SDK can run the loop for you. It does not decide what your agent may do. You do.

---
*Gheware DevOps & Agentic AI · [devops.gheware.com](https://devops.gheware.com)*
