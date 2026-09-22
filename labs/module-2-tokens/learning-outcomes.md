# Learning outcomes &mdash; Module 2: Token optimisation and model selection

*Day 1, block 1.2 &middot; 5 parts &middot; 5 labs*

Tick a box (`- [x]`) when you can do the thing **without looking it up**.

This module assumes you use an AI assistant at work and have a Copilot seat.
It does not teach prompting &mdash; see *What other modules cover* at the foot.

## Progress

| Part | Outcomes | Lab | Done |
|---|:--:|---|:--:|
| 1 &mdash; What one request really costs | 5 | Lab 0 | &#9744; |
| 2 &mdash; Choosing the model, by use case | 5 | Lab 1 | &#9744; |
| 3 &mdash; Routing and cascades | 5 | Lab 2 | &#9744; |
| 4 &mdash; A budget per turn | 5 | Lab 3 | &#9744; |
| 5 &mdash; The levers in your own code | 4 | Lab 4 | &#9744; |

## Part 1 &middot; What one request really costs

- [ ] Write the credit formula from memory and say which of the three token prices is the big one.
- [ ] Name what is metered and what is not, and say what Auto changes.
- [ ] State what happens at zero on an individual plan versus in an organisation &mdash; and say
      which default surprises people.
- [ ] Explain why input is about 100 times output on a bill, in terms of what an agent turn sends
      again.
- [ ] Say why "be concise" is not a cost lever, with a number.

**Lab evidence**
- [ ] Lab 0 &mdash; two bundles metered, the growth of a ten-turn conversation recorded, and you know
      whether your own seat shows you a credit figure at all.

## Part 2 &middot; Choosing the model, by use case

- [ ] Name the six selection criteria, and say which one is not a property of the model tier at all.
- [ ] Explain why the grid is shaded rather than numbered.
- [ ] Place a task on the chart using what being wrong costs and how often the cheap model is
      already right &mdash; and say why placing tasks outlives placing models.
- [ ] Write your prediction down before you look at the evidence, and say what that protects you from.
- [ ] Write a selection rule that says what it is *not* for, and includes its own review trigger.

**Lab evidence**
- [ ] Lab 1 &mdash; three predictions written before the data, scored against it, and one row of a
      model-per-task guide you would defend.

## Part 3 &middot; Routing and cascades

- [ ] Draw the three set-ups and give the cost formula for each in one line.
- [ ] Say why a cascade pays the cheap call even when it escalates, and what that implies.
- [ ] Name four gates that can be automated and two that cannot.
- [ ] Find the escalation rate at which a cascade matches the strong model's accuracy, and the rate
      at which it costs more than not cascading at all.
- [ ] Check whether a cheap model's confidence tracks its correctness, and say what follows if it
      does not.

**Lab evidence**
- [ ] Lab 2 &mdash; accuracy and cost at four thresholds, including the one that costs more than
      always-strong, and the confidence-when-right against confidence-when-wrong figures.

## Part 4 &middot; A budget per turn

- [ ] Explain why the average user tells you nothing about a token bill, using the distribution.
- [ ] Say what to drop first, second, and never.
- [ ] Say what caching rewards, and what a daily edit to an instructions file costs you.
- [ ] Run a context audit that checks the answer again after every cut, and say why checking only at
      the end is not enough.
- [ ] State what a context meter cannot see, without prompting.

**Lab evidence**
- [ ] Lab 3 &mdash; four cuts with tokens and correctness recorded for each, the cut that broke the
      answer identified, and a sentence about what the meter could not see.

## Part 5 &middot; The levers in your own code

- [ ] Rank the levers by saving against effort, and say which two are free.
- [ ] Say why `max_tokens` is on every checklist and near the bottom of this one &mdash; and why it
      is still worth setting.
- [ ] Recognise a model call that is really a computation, and replace it.
- [ ] Argue the variance case, not just the token case, for that replacement.

**Lab evidence**
- [ ] Lab 4 &mdash; a prompt's counting half replaced with standard library, with tokens, wall time
      and whether three runs agreed, plus a statement of what you kept for the model and why.

## Facts that change often

These were checked in September 2026. Check them again before you quote them at work.

- **Credit rates and plan allowances change.** The formula and the three kinds of price have stayed
  the same. The numbers have not. Check slide 4 of the deck against GitHub's current published pricing.
- **The organisation default** is the line most worth checking: extra usage is on by default in an
  organisation and off on an individual plan. If it has changed, it changes what your team pays.
- **No slide names a model.** The model grid is shaded, not numbered, so a new model list does not
  make the deck wrong.
- **The measured workshop day is a record of one past day**, not a forecast. It ran on an open model
  through a gateway, so its money figures are not a Copilot bill. The 99.2% input share is the part
  that carries over.
- **`data/model-runs.json` is made up**, and says so in the file. It lets Lab 1 run offline.
  **Replace it with your own recorded runs before you quote a row as evidence.**
- **`ctxmeter`'s accuracy** was measured on `global-bank-account` on 22 September 2026. See
  `tools/calibration.md`. Measure again after any large change to the repository.

## What other modules cover

This module is about cost and choosing a model. **How to write a good request** is Module 1,
Prompt &amp; context engineering. **What a list of tools costs on every turn** comes back in
Module 4, Agent foundations, tool use and MCP. **Tracing the cost of every agent run** is on Day 3.
