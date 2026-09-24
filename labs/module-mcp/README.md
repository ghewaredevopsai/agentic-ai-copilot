# MCP labs — connect agents to real systems

**Day 3** · five notebook labs · about 2 hours 25 minutes · in the browser sandbox

You give one agent three real systems over MCP: Jira, Langfuse and GitHub. Then you put MCP tools
inside your own ReAct agent, and you protect it from what comes back through them. Every lab runs
on the sandbox model and real servers.

The slides are [`presentation/module-mcp.html`](../../presentation/module-mcp.html).

| Lab | Notebook | Time | The result |
|---|---|:--:|---|
| M.1 OpenCode to Jira, over MCP | `lab-m-1-opencode-jira-over-mcp.ipynb` | 30 min | OpenCode reads the class Jira board and raises a ticket tagged with your sandbox name |
| M.2 Ask your traces | `lab-m-2-langfuse-traces-over-mcp.ipynb` | 25 min | The same agent answers questions about Langfuse traces, and cannot delete anything |
| M.3 Your own repos, your own identity | `lab-m-3-github-your-own-identity.ipynb` | 30 min | The agent works on your GitHub repositories as you, with a read-only token |
| M.4 Langfuse MCP in a ReAct agent | `lab-m-4-langfuse-mcp-in-a-react-agent.ipynb` | 20 min | Your own LangChain agent uses five Langfuse MCP tools to find and explain the slowest step |
| M.5 The bridge, and what comes back through it | `lab-m-5-bridge-and-boundary.ipynb` | 40 min | Without controls, the agent releases a poisoned USD 990,000 payment. With the allow-list and the approval gate, no money moves |

Do M.1 to M.3 in order. They build one `opencode.json` in `~/work/mcplab`, one server at a time.
M.4 and M.5 stand on their own.

The file never holds a secret. It names environment variables instead, so each new terminal needs
the `export` lines the labs print: the Langfuse one from M.2, and your GitHub token in M.3. If
`opencode mcp list` says **needs authentication**, that terminal is missing one of them.

## Before you start

Open a terminal in JupyterLab and check:

```bash
echo "$LAB_LLM_MODEL"
# must print a model name. If it prints nothing, tell your trainer

ls ~/work/agentic-ai-copilot/labs/module-mcp
# must list: README.md and the five lab-m-*.ipynb notebooks
```

**For Lab M.3 only**, you need a GitHub account. The lab shows you how to make a read-only token.

## How the labs work

1. Open a notebook from the file panel on the left. Use the **Python 3** kernel.
2. Run each cell with **Shift + Enter** and read what it prints.
3. Some steps print a command. Paste it into a JupyterLab terminal (**File**, **New**, **Terminal**).
   OpenCode runs there, and you can watch each tool call as it happens.

There is nothing to fill in and nothing is graded. The model is real, so its words change from run
to run. Check what it tells you, especially after it writes something.

**Shared things.** The Jira board and the Langfuse project are shared by the whole class. Put your
sandbox name on anything you create. Langfuse allows about 30 calls a minute for the whole project,
so a "rate limited, waiting" line is normal. The notebook waits and carries on.

Write your notes in `labs/my-work/lab-mcp.md` in this course folder. That folder is yours, and you
do not commit it.

**Words used in these labs**

- **MCP (Model Context Protocol):** a standard way for an agent to use tools in another system.
- **MCP server:** publishes a system's tools over MCP. Here: Jira, Langfuse and GitHub.
- **MCP client:** the part of the agent that talks to servers. OpenCode has one built in.
- **Remote server:** a server that runs somewhere else, reached over HTTP.
- **Tool spec:** a tool's `name`, `description` and `inputSchema`, which is all the model reads.
- **Prompt injection:** text inside data that tries to give the model orders.
- **Allow-list:** the list of fields that may pass. Everything else is dropped.

---
*Gheware DevOps & Agentic AI · [devops.gheware.com](https://devops.gheware.com)*
