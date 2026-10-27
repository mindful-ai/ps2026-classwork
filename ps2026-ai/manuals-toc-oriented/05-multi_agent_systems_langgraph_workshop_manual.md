# Day 23 — Multi-Agent Systems Workshop Manual

## Workshop purpose

This workshop extends the previous tool-using agent into a supervisor-led team of specialized agents. The goal is not to maximize the number of agents: it is to determine when collaboration produces measurable improvement over a simpler baseline.

The primary implementation framework is **LangGraph**. Students also compare LangChain, AutoGen, CrewAI, and Semantic Kernel conceptually.

## Learning outcomes

By the end of the workshop, students will be able to:

- Decide when to use a single workflow, router, supervisor, or role-based team.
- Define planner, specialist, executor, and critic responsibilities.
- Coordinate agents through explicit messages and shared state.
- Resolve conflicting findings and prevent uncontrolled delegation.
- Design reusable agent skills and a consistent execution harness.
- Separate working state, durable memory, and enterprise knowledge.
- Evaluate task completion, handoff quality, tool success, loops, latency, cost, and human escalation.
- Test whether multi-agent collaboration improves on a baseline.

## 1. When do multiple agents help?

Multiple agents help when a task can be usefully decomposed into distinct responsibilities, tools, or expertise areas. They can also increase latency, cost, coordination errors, duplicated work, and the attack surface.

### 1.1 Compare four architectures

| Architecture | How it works | Good fit | Main risk |
|---|---|---|---|
| Single workflow/agent | One controlled flow, possibly with tools | Clear, bounded tasks | One component may become overloaded |
| Router | Selects one path or specialist | Requests fall into distinct categories | Misrouting or poor handling of mixed requests |
| Supervisor | A central controller delegates to specialists and evaluates results | Tasks need decomposition and coordinated synthesis | Supervisor bottleneck or repeated delegation |
| Role-based team | Agents have explicit roles and exchange structured messages | Distinct perspectives, review, or parallel work | Conflicting outputs and coordination overhead |

A supervisor-led team is not automatically better than a router or a single agent. Start with the simplest architecture that meets quality, reliability, latency, and cost requirements.

### 1.2 Decision checklist

Use a multi-agent architecture only when one or more of these claims can be tested:

- The task decomposes into distinct subtasks that can be worked on independently.
- Specialists need different tools or narrowly scoped permissions.
- Parallel work reduces elapsed time enough to justify coordination overhead.
- Independent review measurably catches errors.
- Explicit handoffs improve auditability or operational ownership.

Avoid multi-agent complexity when the workflow is linear, the same context and tools are sufficient, or a deterministic function solves the problem more reliably.

### Hands-on 1

Choose three tasks: a simple FAQ, a support incident investigation, and a policy/compliance review. For each, recommend a single workflow, router, supervisor, or role-based team. State what metric would justify your choice.

## 2. Collaboration design: roles and responsibilities

A useful team has distinct responsibilities and a defined protocol. Do not give every agent the same prompt, all tools, and unrestricted permission to delegate.

### 2.1 Suggested roles

| Role | Responsibility | Typical tools | Must not do |
|---|---|---|---|
| Supervisor | Break down the task, assign work, monitor limits, combine findings | Workflow state and routing | Bypass permissions or delegate indefinitely |
| Planner | Propose a bounded task plan and completion criteria | Usually no external tools | Execute sensitive operations directly |
| Specialist | Investigate a specific domain or evidence source | Narrow, read-only tools | Expand scope beyond its assignment |
| Executor | Perform an authorized, well-defined action | Approved action tools | Perform unapproved writes |
| Critic/reviewer | Check evidence, consistency, policy, and completeness | Evidence and output inspection | Invent evidence or silently rewrite facts |

Not every task needs every role. A practical team may use a supervisor plus two specialists and a reviewer. The executor role can be a deterministic tool layer rather than a separate LLM agent.

### 2.2 Explicit task messages

Use structured messages instead of vague instructions such as “look into this.”

A task message should contain:

- `task_id`: stable identifier for this assignment.
- `goal`: a narrow, testable objective.
- `scope`: permitted data and tools.
- `constraints`: limits, exclusions, and deadlines.
- `expected_output`: schema or required fields.
- `evidence`: references supporting claims.
- `status`: pending, running, completed, failed, or needs-review.

Example:

```python
task_message = {
    "task_id": "ticket-INC-101-retrieval",
    "goal": "Find approved knowledge-base evidence for the VPN issue",
    "scope": {
        "sources": ["approved_knowledge_base"],
        "tools": ["search_docs"]
    },
    "constraints": {
        "max_tool_calls": 4,
        "read_only": True
    },
    "expected_output": {
        "findings": "list",
        "evidence_refs": "list",
        "status": "completed|needs_review|failed"
    },
    "status": "pending"
}
```

Treat the schema above as a simple teaching contract. In production, validate it with Pydantic or an equivalent schema library and enforce authorization in application code.

### 2.3 Shared state

Shared state is the workflow's structured record of task progress. It is not a license for agents to overwrite each other's results.

Recommended fields:

```python
team_state = {
    "request_id": "REQ-001",
    "question": "Investigate intermittent VPN failures",
    "plan": [],
    "assignments": [],
    "findings_by_agent": {},
    "evidence_refs": [],
    "conflicts": [],
    "review_status": "pending",
    "steps": 0,
    "tool_calls": 0,
    "status": "running",
    "final_answer": ""
}
```

Use controlled state updates: each node should write only the fields it owns, or append a typed result that the supervisor validates. Avoid having several agents mutate the same list or dictionary without clear merge rules.

### 2.4 Conflict-resolution rules

Define conflict resolution before running the team:

1. **Evidence beats confidence:** prefer claims with verifiable evidence over unsupported certainty.
2. **Source authority matters:** use the source hierarchy defined by the application.
3. **Check recency and scope:** a current, applicable policy may supersede an older document.
4. **Preserve unresolved conflicts:** do not average contradictory facts or silently choose a side.
5. **Escalate material ambiguity:** ask a human when conflicting evidence changes a consequential decision.
6. **Record the decision:** keep the conflicting claims, source references, resolution rule, and outcome.

### Hands-on 2

Write structured messages for two specialists: one investigates ticket history and another searches approved documentation. Add a conflict case in which their findings disagree. Implement a resolution rule that preserves the conflict if neither source is authoritative.

## 3. Skills and the agent harness

A **skill** is a reusable, bounded capability with a defined input, output, and constraints. A **harness** is the common runtime around agents: it enforces permissions, limits, validation, tracing, error handling, and tool access.

### 3.1 Examples of reusable skills

- `search_approved_docs(query, filters)`
- `lookup_ticket(ticket_id)`
- `summarize_evidence(evidence_items)`
- `check_claim_support(claims, evidence_refs)`
- `calculate_sla_remaining(due_at, now)`

Skills should be independently testable and should not depend on hidden conversational assumptions.

### 3.2 Harness responsibilities

A shared harness should:

- Validate task messages and agent outputs.
- Apply identity-based authorization before tool invocation.
- Enforce tool allowlists, timeouts, and call budgets.
- Normalize tool results and error categories.
- Attach request, task, agent, and trace identifiers.
- Record duration, tool outcome, and relevant cost metrics.
- Redact sensitive fields from logs and traces.
- Prevent agents from invoking arbitrary tools or delegating without limit.

A role prompt is not a security boundary. Permissions must be enforced by the application and tool layer.

### Hands-on 3

Implement one reusable evidence-search skill and call it from two different specialist nodes. Add input validation, a timeout, structured errors, and a shared trace/request ID.

## 4. Memory and state: three separate concepts

Do not treat all information available to an agent as “memory.” Separate these layers:

| Layer | Purpose | Examples | Lifecycle |
|---|---|---|---|
| Working state | Current task progress | Plan, findings, pending action, retries | Usually limited to the workflow/thread |
| Durable memory | Approved information carried across sessions | User preferences, previously resolved issue summaries | Explicit retention and access policy |
| Enterprise knowledge | Authoritative source material | Policies, manuals, tickets, databases, indexed documents | Governed by source ownership and refresh policy |

### 4.1 Isolation and retention requirements

- Scope working state to a task, tenant, user, or authorized conversation.
- Never use a shared thread identifier across unrelated users or tenants.
- Enforce access control when reading durable memory; do not assume the model can safely filter it.
- Set retention and deletion policies for checkpoints, traces, and durable memory.
- Store only information needed for a defined purpose.
- Keep enterprise knowledge in governed source systems and retrieval pipelines, rather than copying entire repositories into agent memory.
- Treat retrieved content as untrusted input; it must not override system policies or tool permissions.

### Hands-on 4

Create a memory policy for the support agent. Identify which fields belong in working state, which (if any) may be retained across sessions, which must remain in enterprise systems, and how user/tenant isolation is enforced.

## 5. Framework awareness and comparison

The following is a practical architectural comparison, not a claim that one framework is best for every workload. Framework features and APIs evolve; check the current official documentation before implementation.

| Framework | Main orientation | Strengths to evaluate | Considerations |
|---|---|---|---|
| LangChain / LangGraph | Model/tool integrations and explicit stateful graph workflows | Typed tool integrations, routing, state, checkpoints, human-in-the-loop | Requires deliberate graph and state design |
| AutoGen | Agent conversations and multi-agent collaboration patterns | Conversational coordination and multi-agent experimentation | Make termination, tool authorization, and workflow boundaries explicit |
| CrewAI | Role/task-oriented agent crews and flows | Intuitive role and task modeling | Ensure control, state, and evaluation remain explicit for complex workflows |
| Semantic Kernel | Enterprise-oriented AI orchestration and plugin/function integration | Integrating AI capabilities into application ecosystems | Fit depends on language/runtime and enterprise integration needs |

### Selection criteria

Evaluate the frameworks against:

- Control over execution and termination.
- State persistence and resumability.
- Human approval support.
- Tool schema validation and permissions.
- Observability and testing.
- Ecosystem and runtime fit.
- Deployment, security, and governance requirements.

For this workshop, use **LangGraph** for the implementation so students can inspect the graph, state, and routing directly. Framework comparison remains an architectural exercise rather than four separate implementations.

### Hands-on 5

Create a one-page decision matrix scoring the four frameworks against the selection criteria above for your organization's use case. Explain which criteria are mandatory and which are preferences.

## 6. Build a supervisor-led team with LangGraph

This lab extends the previous tool-using support-research agent. Begin with deterministic specialist functions and mock data. Add model calls only after routing, state contracts, and stop conditions are tested.

### 6.1 Install dependencies

```bash
pip install -U langgraph langchain-core pydantic
```

Install the selected provider integration separately if you later add an LLM. Store credentials in environment variables or a secret manager, not in source code.

### 6.2 Define a bounded state machine

```text
START
  |
  v
supervisor / planner
  |
  +------> ticket specialist -----+
  |                               |
  +------> knowledge specialist --+--> supervisor
                                      |
                                      v
                                    critic
                                      |
                         +------------+-----------+
                         |                        |
                    needs more work            complete
                         |                        |
                         v                        v
                    supervisor                 finalizer
                                                  |
                                                 END
```

The graph above illustrates the design. The first runnable version below uses sequential specialists for simplicity; a parallel fan-out can be introduced after the baseline is working.

### 6.3 Runnable deterministic starter graph

```python
from typing import TypedDict
from langgraph.graph import StateGraph, START, END

class TeamState(TypedDict):
    question: str
    ticket_id: str
    findings_by_agent: dict[str, list[str]]
    evidence_refs: list[str]
    conflicts: list[str]
    steps: int
    tool_calls: int
    status: str
    final_answer: str

# Mock source data for the workshop.
TICKETS = {
    "INC-101": {
        "summary": "Laptop cannot connect to VPN",
        "status": "open"
    }
}
DOCS = [
    {
        "ref": "KB-17",
        "text": "For intermittent VPN issues, verify network access "
                "and collect the VPN client error before escalating."
    }
]

MAX_STEPS = 6
MAX_TOOL_CALLS = 8

def supervisor_node(state: TeamState) -> dict:
    if state["steps"] >= MAX_STEPS:
        return {"status": "failed"}
    return {"status": "running", "steps": state["steps"] + 1}

def ticket_specialist(state: TeamState) -> dict:
    findings = dict(state["findings_by_agent"])
    ticket = TICKETS.get(state["ticket_id"])
    if ticket is None:
        findings["ticket_specialist"] = ["Ticket not found."]
    else:
        findings["ticket_specialist"] = [
            f"Ticket status: {ticket['status']}.",
            f"Ticket summary: {ticket['summary']}."
        ]
    return {
        "findings_by_agent": findings,
        "tool_calls": state["tool_calls"] + 1
    }

def knowledge_specialist(state: TeamState) -> dict:
    findings = dict(state["findings_by_agent"])
    findings["knowledge_specialist"] = [
        item["text"] for item in DOCS
    ]
    return {
        "findings_by_agent": findings,
        "evidence_refs": ["KB-17"],
        "tool_calls": state["tool_calls"] + 1
    }

def critic_node(state: TeamState) -> dict:
    if state["tool_calls"] > MAX_TOOL_CALLS:
        return {
            "status": "failed",
            "final_answer": "Stopped: tool-call budget exceeded."
        }

    all_findings = [
        item
        for agent_findings in state["findings_by_agent"].values()
        for item in agent_findings
    ]

    if not state["evidence_refs"]:
        return {
            "status": "needs_review",
            "conflicts": ["No evidence references were returned."]
        }

    return {
        "status": "completed",
        "final_answer": (
            "Support summary: " + " ".join(all_findings)
            + " Evidence: " + ", ".join(state["evidence_refs"])
        )
    }

def route_after_supervisor(state: TeamState) -> str:
    if state["status"] == "failed":
        return "end"
    return "ticket_specialist"

def route_after_critic(state: TeamState) -> str:
    if state["status"] == "completed":
        return "end"
    return "end"  # This starter abstains instead of looping indefinitely.

builder = StateGraph(TeamState)
builder.add_node("supervisor", supervisor_node)
builder.add_node("ticket_specialist", ticket_specialist)
builder.add_node("knowledge_specialist", knowledge_specialist)
builder.add_node("critic", critic_node)

builder.add_edge(START, "supervisor")
builder.add_conditional_edges(
    "supervisor",
    route_after_supervisor,
    {"ticket_specialist": "ticket_specialist", "end": END}
)
builder.add_edge("ticket_specialist", "knowledge_specialist")
builder.add_edge("knowledge_specialist", "critic")
builder.add_conditional_edges(
    "critic",
    route_after_critic,
    {"end": END}
)

team = builder.compile()

initial_state: TeamState = {
    "question": "Investigate intermittent VPN failures",
    "ticket_id": "INC-101",
    "findings_by_agent": {},
    "evidence_refs": [],
    "conflicts": [],
    "steps": 0,
    "tool_calls": 0,
    "status": "running",
    "final_answer": ""
}

result = team.invoke(initial_state)
print(result["status"])
print(result["final_answer"])
```

This starter intentionally uses mock data and deterministic specialist functions. It demonstrates graph state and role separation, but it is not yet an LLM-driven supervisor. Before production use, strengthen validation, authorization, error handling, state ownership, and the budget guard on every tool path.

### 6.4 Extend the starter

Add these capabilities one at a time:

1. Replace mock lookups with the validated read-only tools from the previous workshop.
2. Make the supervisor assign structured tasks and choose which specialist to call.
3. Add a critic that checks every material claim against evidence references.
4. Preserve unresolved conflicts and abstain when evidence is insufficient.
5. Add checkpointing and a stable, properly isolated thread ID.
6. Add an approval interrupt before any consequential write operation.
7. Instrument the graph and tools for operational tracing.
8. Add a parallel specialist branch only if it improves measured latency or quality.

### Hands-on 6

Run the starter with a valid ticket and a missing ticket. Add tests for missing evidence, a tool failure, conflicting findings, step-budget exhaustion, and a successful result with evidence references.

## 7. Evaluation: prove whether collaboration helps

The key question is not “Did the agents collaborate?” It is “Did collaboration improve the outcome enough to justify its costs and risks?”

### 7.1 Compare against a baseline

Use the same test set, evidence sources, task requirements, and success criteria for both systems.

- **Baseline:** the previous single tool-using support-research agent.
- **Multi-agent candidate:** supervisor + ticket specialist + knowledge specialist + critic.

Avoid changing the model, prompts, data, and tools all at once; otherwise, it becomes difficult to attribute the improvement to collaboration.

### 7.2 Core metrics

| Metric | Example definition |
|---|---|
| Task completion rate | Completed tasks meeting all required criteria / total tasks |
| Answer correctness | Correct answers according to a reviewed test set |
| Evidence support | Material claims supported by valid evidence references |
| Handoff quality | Assignments with sufficient scope, context, and valid outputs / total handoffs |
| Tool success rate | Successful tool calls / total tool calls |
| Loop rate | Runs stopped by repeated-action or step-budget guards / total runs |
| Latency | Median and p95 end-to-end duration |
| Cost per successful task | Total run cost / successful tasks |
| Human escalation rate | Tasks requiring human intervention / total tasks |
| Recovery success | Recoverable failures that resume or complete safely / injected recoverable failures |

Define each metric before collecting results. Use a fixed test set and report sample size. For small classroom samples, describe results as preliminary rather than statistically conclusive.

### 7.3 Minimal evaluation table

| Test case | Single-agent outcome | Multi-agent outcome | Quality difference | Latency difference | Cost difference |
|---|---|---|---:|---:|---:|
| Straightforward ticket | Record result | Record result | Calculate | Calculate | Calculate |
| Missing evidence | Record result | Record result | Calculate | Calculate | Calculate |
| Conflicting evidence | Record result | Record result | Calculate | Calculate | Calculate |
| Tool timeout | Record result | Record result | Calculate | Calculate | Calculate |
| Approval-required action | Record result | Record result | Calculate | Calculate | Calculate |

Do not invent results. Fill the table from actual runs and retain trace IDs for reproducibility.

### 7.4 Decision rule

Before running the experiment, define a success threshold. For example:

- Correctness or evidence support must improve by a pre-agreed amount, **or** the multi-agent system must materially improve a required capability such as conflict detection.
- Safety, permission enforcement, and approval behavior must not regress.
- Latency and cost must remain within agreed limits.
- If quality is equivalent and cost/latency are worse, retain the simpler baseline.

A multi-agent system may still be justified for auditability, separation of duties, or distinct access boundaries, but those benefits should be stated and evaluated explicitly.

### Hands-on 7

Run at least ten representative test cases against both implementations. Record completion, evidence support, handoff quality, tool failures, loops, latency, cost, and escalation. Write a short recommendation: retain the baseline, adopt the team, or run another experiment.

## 8. Day 23 practical: Role-Based Agent Team

### Scenario

Extend the prior support-research agent into a supervisor-led team. The team investigates a ticket, retrieves approved knowledge, checks the evidence, and produces a recommendation. It must not modify a ticket without explicit human approval.

### Required roles

- **Supervisor:** owns the plan, delegates bounded tasks, enforces budgets, and combines results.
- **Ticket specialist:** uses read-only ticket lookup.
- **Knowledge specialist:** retrieves relevant approved documentation and returns evidence references.
- **Critic:** checks completeness, contradictions, and support for material claims.
- **Executor:** only if an action is approved; executes a validated, authorized operation.

### Required controls

- Typed task messages and validated tool inputs.
- Explicit state ownership and conflict-resolution rules.
- Step, tool-call, time, and cost budgets.
- Bounded retries, structured errors, fallback, and safe abstention.
- Loop detection and clear terminal states.
- Checkpointing and tested resumption.
- Human approval before writes, bound to exact action parameters.
- Observability with sensitive data minimized or redacted.
- Baseline comparison using the same evaluation cases.

### Capstone deliverables

1. Architecture diagram and role/permission matrix.
2. Runnable source code with setup instructions.
3. Unit tests for tools, routing, conflict handling, and stop conditions.
4. Test report covering success and failure scenarios.
5. Evaluation table comparing baseline and multi-agent results.
6. Observability review showing trace IDs, latency, tool outcomes, loops, and costs where available.
7. A short decision memo explaining whether multi-agent collaboration is worth its overhead.

## 9. Suggested implementation sequence

1. **Stage A — Baseline:** run the existing single-agent solution on a fixed test set.
2. **Stage B — Decomposition:** define specialist roles, task contracts, state ownership, and budgets.
3. **Stage C — Deterministic team:** implement supervisor and specialists with mock tools.
4. **Stage D — Secure integration:** connect validated read-only tools and enforce authorization.
5. **Stage E — Review and recovery:** add critic, conflict resolution, fallbacks, and loop detection.
6. **Stage F — Persistence and approval:** add checkpoints and approval-gated writes.
7. **Stage G — Observability:** trace runs while minimizing sensitive data.
8. **Stage H — Evaluation:** compare quality, reliability, latency, cost, and escalation against the baseline.

## 10. Assessment rubric

| Area | Weight |
|---|---:|
| Architecture choice and measurable rationale | 10% |
| Role boundaries and explicit task messages | 15% |
| LangGraph state, routing, and coordination | 20% |
| Secure skills and harness | 10% |
| Memory separation and isolation | 10% |
| Conflict resolution, recovery, and approval | 15% |
| Evaluation quality and baseline comparison | 15% |
| Documentation and reproducibility | 5% |

## 11. Final checklist

- [ ] The team solves a task that benefits from decomposition.
- [ ] The single-agent baseline is measured on the same test set.
- [ ] Every role has a bounded objective and explicit output contract.
- [ ] Tools are validated, authorized, and least-privileged.
- [ ] Shared state has clear ownership and merge rules.
- [ ] Conflicting evidence is preserved or resolved using documented rules.
- [ ] Working state, durable memory, and enterprise knowledge are separate.
- [ ] Memory, checkpoints, and traces are scoped, retained, and accessed under policy.
- [ ] Delegation, steps, tool calls, time, and cost are bounded.
- [ ] Human approval is required for consequential writes.
- [ ] Metrics cover task completion, handoff quality, tool success, loops, latency, cost, and escalation.
- [ ] The final recommendation is based on measured benefit, not agent count.

## References

- LangGraph overview: https://docs.langchain.com/oss/python/langgraph/overview
- LangGraph persistence: https://docs.langchain.com/oss/python/langgraph/persistence
- LangGraph human-in-the-loop: https://docs.langchain.com/oss/python/langgraph/interrupts
- LangChain tools: https://docs.langchain.com/oss/python/langchain/tools
- AutoGen documentation: https://microsoft.github.io/autogen/
- CrewAI documentation: https://docs.crewai.com/
- Semantic Kernel documentation: https://learn.microsoft.com/semantic-kernel/
- LangSmith documentation: https://docs.smith.langchain.com/

Check current official documentation for API changes before using examples in production. The code in this manual is a teaching starter; mock integrations must be replaced with secure, authorized, and observable implementations for real workloads.
