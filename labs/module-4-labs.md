# Module 4 labs — Agent foundations and tool use

**Day 1** · Labs 4.1, 4.2 and 4.3 · about 75 minutes · **Day 2** · Lab 4.4 · about 15 minutes ·
Folder: `labs/module-4-agent/` in this course folder

In Module 3 you built AskOps. Its `/api/ask` endpoint runs the same two searches every time. In these
labs AskOps becomes an agent: a model chooses which tool to call next, and your code runs it.

- **Lab 4.1** reads and runs a complete agent loop in plain Python, about 100 lines, with no framework.
- **Lab 4.2** breaks that agent in five ways on purpose, fixes each one, and counts the tokens each fix
  saves.
- **Lab 4.3** builds the same agent on the **GitHub Copilot SDK**, where Copilot runs the loop, and
  compares the two.
- **Lab 4.4, on Day 2,** runs your fixed agent on a real model in the sandbox.

On Day 1 there is no model endpoint on your machine, so Labs 4.1 and 4.2 use a fake model and Lab 4.3
uses your Copilot seat. The real-model runs wait for the Day 2 sandbox.

## Words used in these labs

Slide 3 of the Module 4 deck has the full list. The ones you need most:

- **Tool call:** the model's request to run one tool with some arguments. Your code decides whether
  to run it.
- **Observation:** the tool's result, sent back to the model as a message.
- **Step:** one round trip to the model. **Step budget:** the most steps one run may take.
- **Fake model:** `fake_llm.py`, a small server that replays a script. It is not an AI. It lets you
  cause each failure on demand, and it works with no network.

## Before you start

You need **Python 3.14** (3.11 or newer works), a bash terminal and VS Code with Copilot. Labs 4.1 and
4.2 use only the Python standard library, so there is **nothing to install**.

Open **two terminals**, both in the lab folder:

```bash
cd <this course folder>/labs/module-4-agent
ls
# must list: agent.py  agent_sdk.py  askops_data.json  fake_llm.py  solutions
```

Terminal 1 runs the model. Terminal 2 runs the agent. Your notes go in
`labs/my-work/lab-4-agent.md`. That folder is yours, and you do not commit it.

**Do not open `solutions/` until the end of Lab 4.2.** It holds one answer to every fix.

---

## Lab 4.1 — Read the loop, then run it

**Goal:** see every message an agent sends and receives · **Timebox:** 12 min · **Output:** three
answers and a token count in `labs/my-work/lab-4-agent.md`

### Step 1 — Read `run()` before you run it (7 min)

Open `agent.py`. Find `run()` near the bottom. It is the same loop as slide 14.

**Prompt 4-A** · Ask mode · base model · **new chat**

```text
Explain the run() function in labs/module-4-agent/agent.py, line by line.
Then answer:
1. Which line is the "reason" step, which is "act" and which is "observe"?
2. How does the loop know the model has finished?
3. What does the loop send to the model on the second call that it did not send on the first?
Do not change any file.
```

Check Copilot's answers against the code yourself. Write your own three answers in your notes.

### Step 2 — Run it on the fake model (5 min)

Terminal 1:

```bash
python fake_llm.py happy
# prints: Fake model on http://127.0.0.1:4000/v1, scenario 'happy'.
```

Terminal 2:

```bash
python agent.py
```

**What you should see:** two steps with ACTION lines, then an answer that cites RB-101 and says
INC-9001 is already open. The last line reads `[3 steps, ... tokens]`.

Now look at Terminal 1. It printed one line per call. **The number of messages and the tokens go up
on every call**, because the agent sends the whole list again each time (slide 15). Write the three
token numbers in your notes.

### If you are behind

Do Step 2 only. Read the Terminal 1 lines and note how the tokens grow.

---

## Lab 4.2 — Make it fail, fix it, count the tokens

**Goal:** cause five common agent failures on purpose, fix each in code, and measure what the fix
saves · **Timebox:** 35 min · **Output:** the table below, filled in, in
`labs/my-work/lab-4-agent.md`

Copy this table into your notes first:

```text
| Scenario | Before the fix: what happened | Steps | Tokens | After the fix: what happened | Steps | Tokens |
|----------|-------------------------------|-------|--------|------------------------------|-------|--------|
| invented |                               |       |        |                              |       |        |
| badargs  |                               |       |        |                              |       |        |
| loop     |                               |       |        |                              |       |        |
| write    |                               |       |        |                              |       |        |
```

**How every scenario works:** start the fake model with the scenario name in Terminal 1, run
`python agent.py` in Terminal 2, and record the result. Then fix `agent.py` with Copilot, and run
it again **against the same scenario**. Restart the fake model with Ctrl+C, then the next scenario
name, between scenarios.

A crash also counts as a result. Write down the error, then mark the steps and tokens as "crashed".

### Step 1 — The invented tool and the wrong argument (10 min)

Run `python fake_llm.py invented`, then `python agent.py`. Then do the same with `badargs`.

**What you should see:** both crash. `invented` stops with `KeyError: 'open_ticket'`. The model
asked for a tool that does not exist. `badargs` stops with a `TypeError`. The model used the right
tool with an argument name the tool does not have. The line marked `# no checks yet` trusted both.

**Prompt 4-B** · Agent mode · base model · **new chat**

```text
In labs/module-4-agent/agent.py, the line marked "# no checks yet" runs any tool call the model sends.
Add a function run_tool(name, raw_args) and call it from that line. It must:
- return "ERROR: no tool called <name>." if the tool does not exist
- return "ERROR: bad arguments for <name>: <reason>" if the arguments are not valid JSON,
  or do not match the function (TypeError)
- otherwise run the tool and return its result
It must never raise. The error text goes back to the model as the observation.
Change only agent.py. Keep the standard library only.
```

Review the diff before you keep it. Then run both scenarios again.

**What you should see now:** no crash. In `invented`, the model reads the error and answers without
the missing tool. In `badargs`, it reads the error, calls `get_runbook` again with `runbook_id`, and
answers. This is slide 12: return the error as the observation, and the model usually corrects
itself.

### Step 2 — The loop (8 min)

Run `python fake_llm.py loop`, then `python agent.py`.

**What you should see:** `list_incidents` six times, then `Stopped: step budget spent.` The step
budget saved you, but you paid for six calls, and each one was bigger than the last. Write down the
tokens.

**Prompt 4-C** · Agent mode · base model · **same chat**

```text
In run(), stop the loop as soon as the model makes the same tool call twice: the same tool name with
the same arguments string. Return "Stopped: <name> called twice with the same arguments." with the
step number and the tokens used, like the other return lines. Change only agent.py.
```

Run the `loop` scenario again. Compare the tokens with your first run. You should see the run stop
at step 2, with a small part of the tokens.

### Step 3 — The write that nobody approved (7 min)

Run `python fake_llm.py write`, then `python agent.py`.

**What you should see:** the agent opens a new incident, INC-9004, for a problem INC-9001 already
covers. Nobody was asked. This is slide 8: a tool that writes needs a person's approval, enforced in
code.

**Prompt 4-D** · Agent mode · base model · **same chat**

```text
In run_tool(), before open_incident runs, show the arguments and ask the person at the terminal
"Approve open_incident <args>? [y/N]". Run the tool only if they type y. Otherwise return
"ERROR: a person refused. Do not open an incident." Change only agent.py.
```

Run the scenario twice: type `n` once and `y` once. With `n`, the agent reports that it did not open
an incident.

### Step 4 — The token budget, and the error hidden as empty (8 min)

These two need no fake scenario.

**Token budget.** The step budget limits steps, not cost.

**Prompt 4-E** · Agent mode · base model · **same chat**

```text
Add MAX_TOKENS = 8000 next to MAX_STEPS in agent.py. After each step, if the tokens used so far are
above MAX_TOKENS, stop and return "Stopped: token budget spent." with the step and tokens.
Change only agent.py.
```

To test it, set `MAX_TOKENS = 500` for one run of the `happy` scenario. It should stop early. Put it
back to 8000.

**The error hidden as empty.** Read `search_runbooks()`. When `SEARCH_DOWN` is set, it pretends the
runbook source is down, and returns `[]`, an empty list. Try it:

```bash
python -c "import os; os.environ['SEARCH_DOWN']='1'; import agent; print(agent.search_runbooks('502 deploy'))"
# prints: []
```

To the model, `[]` means "no runbook matches". It will tell the engineer there is no runbook, while
the real problem is that the source is down. Module 3 had the same bug in `/api/ask`, and its fix was
a 503. Change the line so it returns `"ERROR: runbook search is unavailable. Try again later."`
instead. You can do this one by hand.

### Step 5 — Compare with the solution (2 min)

Now open `solutions/agent.py`. It marks each fix with `Fix 1` to `Fix 5`. Yours can differ. What
matters is that each scenario now ends with an answer or a clear stop, never a crash.

### If you are behind

Do Steps 1 and 2. Run the other scenarios against `solutions/agent.py` to see the fixed behaviour:
`python solutions/agent.py`.

---

## Lab 4.3 — The same agent on the Copilot SDK

**Goal:** give the same tools to Copilot's own agent loop, and compare what you write with what it
hides · **Timebox:** 25 min · **Output:** the comparison table below in
`labs/my-work/lab-4-agent.md`

The **GitHub Copilot SDK** lets a Python program use your Copilot subscription as the agent's model.
Copilot runs the loop. You give it the tools and decide what they may do. `agent_sdk.py` imports the
tool functions from `agent.py`, so the tools are exactly the same. Only the loop changes.

**Every run uses your Copilot allowance**, like a chat in VS Code.

### Step 1 — Set up (8 min)

The SDK needs the **Copilot CLI** and your sign-in. Your trainer confirms on the day that your
company allows the Copilot CLI. If it does not, pair with someone whose machine works, or follow
the trainer's screen, and still fill in the table.

1. Install the Copilot CLI, and sign in once:

   ```bash
   npm install -g @github/copilot      # or on Windows: winget install GitHub.Copilot
   copilot
   # inside it, type /login, follow the browser steps, then /exit
   ```

2. Install the SDK in a virtual environment:

   ```bash
   cd <this course folder>/labs/module-4-agent
   python -m venv .venv
   source .venv/bin/activate          # Git Bash on Windows: source .venv/Scripts/activate
   pip install github-copilot-sdk
   ```

3. Point the SDK at the CLI you installed:

   ```bash
   export COPILOT_CLI_PATH="$(command -v copilot)"
   ```

   Without this, the SDK downloads its own copy of the runtime from GitHub on the first run.

### Step 2 — Run it (5 min)

```bash
python agent_sdk.py
```

**What you should see:** ACTION lines for the tools Copilot chose, an answer that cites RB-101, and
`[... model calls, ... tokens]`. The model is `gpt-5-mini` unless your trainer names another. To
change it, run `export ASKOPS_MODEL=<name>`.

Now ask for a write:

```bash
python agent_sdk.py "Disk on the report nodes is at 95 percent and nobody has opened an incident. Open one."
```

The SDK stops and asks you to approve `open_incident`. Type `n` once. Then run it again and type
`y`. Find the function that asked you. It is `approve()`, in your code, not in Copilot.

Last, ask for something outside its tools:

```bash
python agent_sdk.py "Run the shell command ls and tell me what it prints."
```

It refuses. Copilot normally has shell and file tools. `available_tools=ToolSet().add_custom("*")`
switched them all off, so it can use only your four tools. This is slide 8 again: you decide what
the agent may do.

### Step 3 — Compare the two (10 min)

Read `agent_sdk.py` next to `solutions/agent.py`. Fill in:

```text
| Question                                         | agent.py (plain loop) | agent_sdk.py (Copilot SDK) |
|--------------------------------------------------|-----------------------|----------------------------|
| How many lines are the loop itself?              |                       |                            |
| Where is the step budget?                        |                       |                            |
| Can you print the message list sent to the model?|                       |                            |
| Where does the approval for open_incident live?  |                       |                            |
| How do you count tokens per run?                 |                       |                            |
| What happens if the model invents a tool?        |                       |                            |
| Which one would you debug more easily, and why?  |                       |                            |
```

There are no single right answers. What you should notice: the SDK saves you writing the loop, but
you can no longer see or change each step of it. The things that keep the agent safe are still
your code: which tools exist, which ones need approval, and the token count.

### If you are behind

Skip Step 1 and read `agent_sdk.py` alongside the trainer's run. Fill in the table from the code.

---

## Lab 4.4 — On Day 2: the same agent on a real model

**Goal:** see how a real model's path differs from the fake model's script, and check your fixes
against it · **When:** Day 2, in the browser sandbox · **Timebox:** 15 min · **Output:** a new
section in `labs/my-work/lab-4-agent.md`

The sandbox already knows where its model is. It sets `LAB_LLM_BASE_URL` and `LAB_LLM_MODEL`, and
`agent.py` reads them, so there is nothing to configure.

### Step 1 — Bring your agent to the sandbox (3 min)

Open a terminal in the sandbox, go to `labs/module-4-agent/` in this course folder, and check:

```bash
echo "$LAB_LLM_MODEL"
# must print a model name. If it prints nothing, tell your trainer
```

The `agent.py` here is the untouched starter. Save your fixed Day 1 version next to it as
**`my_agent.py`**: open a new file with that name and paste your code in. It is the one with
`run_tool()` and the loop check. If you do not have it, copy `solutions/agent.py` to `my_agent.py`
and change `.parent.parent` to `.parent` in its `DATA =` line, so it finds the data file.

### Step 2 — Run it twice, on the same question (5 min)

```bash
python my_agent.py
python my_agent.py
python my_agent.py "Logins are slow this morning. Is there a runbook?"
```

Do **not** start `fake_llm.py`. Write down the ACTION lines, steps and tokens of each run.

**What you should see:** the two runs of the same question may choose different tools, or a
different order. The fake model always followed its script, but a real model chooses its path at
run time (slide 5). Compare the tokens with your Lab 4.1 numbers.

### Step 3 — The error hidden as empty, for real (4 min)

Run the starter and your fixed agent with the search source "down":

```bash
SEARCH_DOWN=1 python agent.py "Payments returns 502s after the release. What do I do?"
SEARCH_DOWN=1 python my_agent.py "Payments returns 502s after the release. What do I do?"
```

With `[]`, the starter's model usually says no runbook exists. With the error text, it should
say that search is unavailable. That difference is the whole point of Fix 5.

### Step 4 — Change one description (3 min)

In `my_agent.py`, in `TOOL_SPECS`, change the description of `get_runbook` to `"Gets data."`. Run
the Step 2 questions again. Does the agent still call the right tools? Put the description back afterwards.

This agent is also where Day 2 starts. In the LangChain lab you rebuild it with a framework and
compare the two.

---

## What you take away

- An agent is a loop. The model chooses the next step. Your code runs every tool.
- Every call resends the whole message list, so tokens per call go up at every step.
- Check every tool call before you run it, and send errors back as observations. Never crash.
- A loop needs all four stop conditions: an answer, a step budget, a loop check and a way to hand
  over. Add a token budget too.
- A tool that writes needs a person's approval, enforced in code.
- A framework or an SDK can run the loop for you. It does not decide what your agent may do. You do.

On Day 2 you run it on a real model (Lab 4.4), then rebuild it with LangChain and LangGraph, and
compare again.

---
*Gheware DevOps & Agentic AI · [devops.gheware.com](https://devops.gheware.com)*
