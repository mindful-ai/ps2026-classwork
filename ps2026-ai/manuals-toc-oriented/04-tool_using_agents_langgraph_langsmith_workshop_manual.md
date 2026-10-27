# Day 22 — Tool-Using Agents Workshop Manual

## Workshop purpose

This workshop moves from simple LLM calls to controlled, stateful agents that use tools, manage execution, recover from failures, and request human approval for sensitive actions.

The guiding principle is to define the agent's objective, permissions, state, and stopping rules **before** choosing a framework.

## Learning outcomes

By the end of the workshop, students will be able to:

- Design an agent with a bounded objective, explicit state, tools, permissions, and stop conditions.
- Build typed and validated tools for APIs, databases, and calculations.
- Implement planner-executor workflows with LangGraph nodes, edges, and conditional routing.
- Add checkpoints, resumability, bounded retries, fallbacks, and loop detection.
- Pause execution for human approval before sensitive actions.
- Trace prompts, tool calls, state transitions, latency, and cost using LangSmith.
- Build and test a stateful research or support agent.

## 1. Agent design: objective, state, tools, and boundaries

An agent is more than an LLM with tools. It combines a model with a controlled execution loop.

### 1.1 Define the agent contract

Before implementation, document:

| Design element | Example |
|---|---|
| Objective | Research a technical issue and produce an evidence-backed answer |
| State | Request, plan, findings, errors, task status, iteration count |
| Tools | Search approved documents, query an approved database, calculate statistics |
| Permissions | Read-only by default; no unrestricted shell or database writes |
| Stop conditions | Goal achieved, iteration budget exhausted, or unrecoverable failure |
| Escalation | Ask a human when evidence is insufficient or an action is sensitive |
| Deterministic boundaries | Fixed tool schemas, timeouts, maximum calls, and output validation |

### 1.2 Define stop conditions before selecting a framework

An agent must not run indefinitely because a model continues requesting actions. Use deterministic limits outside the model.

```python
MAX_STEPS = 8
MAX_TOOL_CALLS = 12

def should_stop(state):
    if state["status"] in {
        "completed", "failed", "waiting_for_approval"
    }:
        return True
    if state["steps"] >= MAX_STEPS:
        return True
    if state["tool_calls"] >= MAX_TOOL_CALLS:
        return True
    return False
```

This is a basic guard. Production systems should also enforce wall-clock deadlines, per-tool timeouts, cost limits, and authorization checks outside the model.

### Hands-on 1

Design an agent that investigates a support ticket. Write down its objective, state fields, permitted tools, prohibited actions, maximum iterations, and conditions requiring human intervention.

## 2. Tool engineering: typed and secure tools

Tools are the agent's interface to the outside world. Their contracts should be explicit, predictable, and independently testable.

### 2.1 Build a validated calculation tool

```python
from pydantic import BaseModel, Field

class PercentageChangeInput(BaseModel):
    old_value: float = Field(ge=0)
    new_value: float = Field(ge=0)

def percentage_change(data: PercentageChangeInput) -> dict:
    if data.old_value == 0:
        return {
            "ok": False,
            "error": "Cannot calculate percentage change from zero."
        }

    change = (
        (data.new_value - data.old_value) / data.old_value
    ) * 100

    return {
        "ok": True,
        "percentage_change": round(change, 2)
    }

result = percentage_change(
    PercentageChangeInput(old_value=100, new_value=125)
)
print(result)
```

Expected result:

```text
{'ok': True, 'percentage_change': 25.0}
```

### 2.2 Secure-tool checklist

- **Least privilege:** grant only the permissions needed for the task.
- **Input validation:** validate types, lengths, identifiers, and allowed values.
- **Timeouts:** prevent stalled API calls or database queries from blocking execution.
- **Auditing:** record tool name, validated arguments, outcome, duration, and request ID.
- **Safe errors:** return structured errors rather than stack traces, credentials, or internal configuration.
- **Untrusted data:** treat retrieved pages and documents as data, not instructions that override policy.
- **Database safety:** use parameterized queries and restricted database accounts.
- **Writes:** separate preparation from execution and require approval for consequential actions.

### 2.3 Example: validated ticket lookup

```python
from pydantic import BaseModel, Field

class TicketLookupInput(BaseModel):
    ticket_id: str = Field(
        min_length=3,
        max_length=32,
        pattern=r"^[A-Za-z0-9_-]+$"
    )

# Demo data stands in for an approved read-only database.
TICKETS = {
    "INC-101": {
        "status": "open",
        "summary": "Laptop cannot connect to VPN"
    }
}

def lookup_ticket(data: TicketLookupInput) -> dict:
    ticket = TICKETS.get(data.ticket_id)
    if ticket is None:
        return {"ok": False, "error": "Ticket not found"}
    return {"ok": True, "ticket_id": data.ticket_id, **ticket}

print(lookup_ticket(TicketLookupInput(ticket_id="INC-101")))
```

This is a local demonstration, not a production database connector. A real connector should enforce identity-based access, query timeouts, logging, and data minimization.

### Hands-on 2

Implement `lookup_ticket(ticket_id)` and `calculate_sla_remaining(due_at, now)`. Validate inputs, return consistent success/error structures, and test malformed IDs, missing tickets, and invalid timestamps.

## 3. Agent workflow: LangGraph state machine

LangGraph represents a workflow as state, nodes, and edges. Nodes perform work; edges determine what runs next. Conditional edges route based on the current state.

### 3.1 Install the core dependencies

Run in the same Python environment as the notebook or script:

```bash
pip install -U langgraph langchain-core pydantic
```

For model-backed planning, install the integration for the chosen provider, such as `langchain-openai`, and configure its API key through an environment variable. Do not hard-code secrets in notebooks or source control.

### 3.2 Understand the graph

A bounded planner-executor workflow can look like this:

```text
START
  |
  v
plan
  |
  v
execute
  |
  v
evaluate
  |------------------|
  | more work needed | done / limit reached
  v                  v
plan               END
```

The graph should not give the planner unlimited control. The workflow code owns limits and policy decisions.

### 3.3 Minimal runnable LangGraph example

This example uses deterministic mock tools so students can learn the graph mechanics without API keys.

```python
from typing import TypedDict
from langgraph.graph import StateGraph, START, END

class AgentState(TypedDict):
    question: str
    plan: list[str]
    findings: list[str]
    steps: int
    status: str
    answer: str

def plan_node(state: AgentState) -> dict:
    # A deterministic plan for learning purposes.
    if not state["plan"]:
        return {
            "plan": ["search approved notes", "summarize findings"],
            "status": "running"
        }
    return {"status": "running"}

def execute_node(state: AgentState) -> dict:
    # Mock retrieval tool; replace with an authorized tool later.
    findings = list(state["findings"])
    if not findings:
        findings.append(
            "Mock evidence: the service reports intermittent VPN failures."
        )
    return {
        "findings": findings,
        "steps": state["steps"] + 1
    }

def evaluate_node(state: AgentState) -> dict:
    if state["findings"]:
        return {
            "status": "completed",
            "answer": (
                "Based on the available mock evidence: "
                + " ".join(state["findings"])
            )
        }
    if state["steps"] >= 3:
        return {
            "status": "failed",
            "answer": "Stopped because the step budget was reached."
        }
    return {"status": "running"}

def route_after_evaluate(state: AgentState) -> str:
    if state["status"] in {"completed", "failed"}:
        return "end"
    if state["steps"] >= 3:
        return "end"
    return "execute"

builder = StateGraph(AgentState)
builder.add_node("plan", plan_node)
builder.add_node("execute", execute_node)
builder.add_node("evaluate", evaluate_node)

builder.add_edge(START, "plan")
builder.add_edge("plan", "execute")
builder.add_edge("execute", "evaluate")
builder.add_conditional_edges(
    "evaluate",
    route_after_evaluate,
    {"execute": "execute", "end": END}
)

graph = builder.compile()

initial_state: AgentState = {
    "question": "Why is the VPN connection failing?",
    "plan": [],
    "findings": [],
    "steps": 0,
    "status": "running",
    "answer": ""
}

result = graph.invoke(initial_state)
print(result["status"])
print(result["answer"])
```

This mock workflow teaches state flow and routing. It is intentionally not an autonomous LLM agent yet. Replace the deterministic planner and mock retrieval with model/tool calls only after the state contract and controls are tested.

### 3.4 Add model-backed planning safely

A production planner may use an LLM to suggest the next action, but its output should be constrained to an allowlisted action schema. The model proposes; application code validates and authorizes.

Example action contract:

```python
from typing import Literal
from pydantic import BaseModel, Field

class ProposedAction(BaseModel):
    action: Literal["search_docs", "lookup_ticket", "finish"]
    query: str = Field(default="", max_length=300)
    rationale_summary: str = Field(default="", max_length=300)
```

The orchestrator must reject unknown actions, validate arguments, enforce call budgets, and ensure that the selected tool is permitted for the current user and task.

### Hands-on 3

Extend the graph with a `retrieve` node and a `summarize` node. Add a conditional route that ends when evidence is sufficient, or stops after a maximum of four execution steps. Write tests for both routes.

## 4. Checkpoints and resumable execution

Checkpoints persist graph state so an interrupted workflow can continue from a saved point. They are useful for long-running research, human approvals, and transient tool failures.

### 4.1 In-memory checkpoint demonstration

```python
from langgraph.checkpoint.memory import InMemorySaver

# Use the same StateGraph builder from the previous example.
# Compile with a checkpointer:
checkpointer = InMemorySaver()
graph_with_checkpoints = builder.compile(checkpointer=checkpointer)

config = {
    "configurable": {
        "thread_id": "support-ticket-demo-001"
    }
}

result = graph_with_checkpoints.invoke(initial_state, config=config)
print(result["status"])
```

The same `thread_id` identifies a conversation/workflow thread. The in-memory saver is suitable for learning and tests; its state does not survive process loss. For production, choose a durable checkpointer supported by your deployment, secure stored state, define retention rules, and control access to checkpoint data.

### 4.2 Resumability checklist

1. Assign a stable, non-secret thread ID.
2. Persist the minimum state required to resume.
3. Make tools idempotent where possible, so replay does not duplicate side effects.
4. Store operation IDs or idempotency keys for external writes.
5. Define what happens if the process stops during a tool call.
6. Test resumption from a checkpoint and verify that completed side effects are not repeated.

## 5. Reliability controls

### 5.1 Bounded retries and fallbacks

Retry only errors that may be transient, such as rate limits or temporary network failures. Do not blindly retry invalid input, permission denials, or deterministic business-rule failures.

```python
import time

def call_with_bounded_retries(
    operation,
    max_attempts=3,
    delay_seconds=0.5
):
    last_error = None

    for attempt in range(max_attempts):
        try:
            return operation()
        except (TimeoutError, ConnectionError) as exc:
            last_error = exc
            if attempt < max_attempts - 1:
                time.sleep(delay_seconds * (2 ** attempt))

    return {
        "ok": False,
        "error": "Temporary service failure",
        "attempts": max_attempts
    }
```

In a real system, add jitter, an overall deadline, provider-specific retry rules, and a circuit breaker when appropriate. Do not expose raw exception text to the end user. The demonstration catches only selected transient errors; adapt the exception list to the client library.

### 5.2 Fallback strategy

A fallback must preserve the safety contract. Examples:

- Primary search API unavailable → search an approved local knowledge base.
- Reranker unavailable → use the original retrieval ranking and disclose the reduced confidence.
- Evidence insufficient → ask a clarifying question or abstain.
- Tool permission denied → stop or request authorized approval; do not try a more privileged tool.

### 5.3 Loop detection

Detect repeated actions or repeated state transitions. A simple guard can track action signatures:

```python
def repeated_action(action_signature, recent_actions, max_repeats=2):
    recent = recent_actions[-max_repeats:]
    return (
        len(recent) == max_repeats
        and all(item == action_signature for item in recent)
    )
```

Use this alongside step budgets, tool-call budgets, and deadline limits. A loop detector is a safety net, not a replacement for bounded execution.

### 5.4 Human approval

Require explicit approval before high-impact actions such as sending external messages, changing records, issuing refunds, or running a destructive operation.

A safe sequence is:

1. Agent prepares a proposed action and explains its user-facing impact.
2. Application validates the action and shows the exact parameters to the approver.
3. Execution pauses and stores the pending action.
4. An authorized human approves or rejects it.
5. The application revalidates permissions and executes only the approved action.
6. The decision and result are audited.

Approval must be bound to the exact action and parameters. If the action changes after approval, request approval again.

### Hands-on 4

Add a `pending_action` field and an approval route to the workflow. The agent may propose a ticket update, but must not execute it until an approval flag is supplied. Test approval, rejection, timeout, and modified-after-approval cases.

## 6. LangSmith observability

LangSmith helps trace LLM application runs, including model calls and tool execution, when the application is instrumented and configured. Use traces to debug behavior and measure performance—not to collect sensitive data indiscriminately.

### 6.1 Typical setup

Install the package:

```bash
pip install -U langsmith
```

Configure tracing using environment variables in your shell or secret manager. For example, set the tracing enablement flag and API key according to the current LangSmith documentation. Keep secrets out of notebooks, logs, screenshots, and source control. Configure the project name and endpoint as required by your environment.

### 6.2 What to observe

| Signal | Why it matters |
|---|---|
| Run and trace IDs | Correlate a request across components |
| Node and state transitions | Find routing mistakes and loops |
| Tool name and outcome | Identify failing integrations |
| Latency per node/tool | Find bottlenecks |
| Retry count | Detect unstable dependencies |
| Token usage and model cost | Track operational cost |
| Final status and error category | Monitor reliability |
| Approval wait time | Understand human-in-the-loop delays |

### 6.3 Privacy-conscious tracing

- Do not log API keys, passwords, session cookies, or access tokens.
- Minimize or redact personal data and sensitive customer content.
- Avoid recording hidden chain-of-thought. Capture concise decision summaries, selected action names, validated arguments, and outcomes instead.
- Set retention and access controls for traces.
- Use synthetic data for teaching and test environments.
- Document what is sent to external observability services and verify organizational policy before enabling tracing.

### Hands-on 5

Instrument the agent and run three test cases: a successful lookup, a transient tool failure, and an approval-required action. Compare node latency, tool outcomes, retry counts, and final statuses. Redact sensitive fields before sending traces.

## 7. Day 22 practical: Stateful Agent Lab

### Scenario

Build a support-research agent that receives a ticket ID and question, retrieves ticket details and approved knowledge-base evidence, and returns a concise recommendation with evidence. It may propose a ticket update but cannot write the update without human approval.

### Suggested architecture

```text
User request
    |
    v
Validate request and permissions
    |
    v
Plan next step
    |
    v
Route to approved read-only tools
    |
    v
Collect evidence and evaluate
    |                |
 sufficient       insufficient
    |                |
    v                v
Draft answer       bounded retry / clarify / abstain
    |
    v
Optional proposed write
    |
    v
Human approval gate
    |
    v
Execute approved action or reject
    |
    v
Final response + audit record
```

### Required state

```python
class LabState(TypedDict):
    request_id: str
    question: str
    ticket_id: str
    plan: list[str]
    findings: list[str]
    steps: int
    tool_calls: int
    errors: list[str]
    pending_action: dict | None
    approval_status: str
    status: str
    answer: str
```

Add imports for `TypedDict` and any other types used by your Python version. In Python versions before 3.10, use `Optional[dict]` instead of `dict | None`.

### Minimum requirements

- [ ] Typed input validation for each tool.
- [ ] Read-only tools for ticket and knowledge lookup.
- [ ] LangGraph nodes and conditional edges.
- [ ] Maximum step and tool-call limits.
- [ ] Per-tool timeout and bounded transient retries.
- [ ] Structured error handling and fallback behavior.
- [ ] Loop detection and a clear terminal status.
- [ ] Checkpointing with a stable thread ID.
- [ ] Human approval before any write operation.
- [ ] LangSmith traces with sensitive values minimized or redacted.
- [ ] Tests for success, missing evidence, tool failure, loop, rejection, and resume.

### Suggested implementation stages

1. **Stage A — Deterministic foundation:** implement state, mock tools, routing, and stop conditions.
2. **Stage B — Secure tools:** add schema validation, least-privilege access, timeouts, and structured results.
3. **Stage C — Model integration:** use an LLM for planning or synthesis, with an allowlisted action schema.
4. **Stage D — Reliability:** add retries, fallbacks, loop detection, and checkpoints.
5. **Stage E — Approval:** pause for approval and bind approval to the exact proposed action.
6. **Stage F — Observability:** trace runs and review latency, errors, costs, and state transitions.
7. **Stage G — Evaluation:** run the test matrix and report the results.

### Test matrix

| Test | Expected behavior |
|---|---|
| Valid ticket and evidence found | Return an evidence-backed recommendation |
| Unknown ticket | Return a structured not-found response |
| Search API times out | Retry within limits, then use approved fallback or stop |
| No supporting evidence | Ask a clarifying question or abstain |
| Planner repeats an action | Loop guard or step budget stops execution |
| Tool permission denied | Stop safely; do not escalate privileges automatically |
| Write action proposed, approval pending | Pause without executing the write |
| Human rejects action | Record rejection and return a safe result |
| Checkpoint resume | Continue from saved state without duplicating side effects |
| Sensitive data in inputs | Redact or minimize it in traces |

### Capstone deliverables

1. Architecture diagram and agent contract.
2. Runnable source code and dependency list.
3. Unit tests for tools and routing.
4. Test report covering all required failure cases.
5. A trace review showing latency, tool outcomes, retries, and cost where available.
6. Short security review documenting permissions, sensitive data, and approval boundaries.

## 8. Assessment rubric

| Area | Weight |
|---|---:|
| Objective, state, permissions, and stop conditions | 15% |
| Typed and secure tools | 15% |
| LangGraph workflow and routing | 20% |
| Checkpoints and resumability | 10% |
| Reliability and recovery | 15% |
| Human approval and auditability | 10% |
| Observability and evaluation | 10% |
| Code clarity and documentation | 5% |

## 9. Final checklist

- [ ] The objective is narrow and testable.
- [ ] The model cannot invent new tools or bypass application authorization.
- [ ] Every tool has validated inputs, bounded execution time, and structured outputs.
- [ ] Step, tool-call, time, and cost budgets are enforced outside the model.
- [ ] Errors are classified as transient, permanent, or policy-related.
- [ ] Repeated actions and failed loops are detected.
- [ ] Checkpoints are secured and resumption does not duplicate side effects.
- [ ] Consequential actions require explicit, action-specific approval.
- [ ] Traces capture operational signals without exposing hidden reasoning or secrets.
- [ ] Tests cover both successful and failure paths.

## References

- LangGraph documentation: https://docs.langchain.com/oss/python/langgraph/overview
- LangGraph persistence: https://docs.langchain.com/oss/python/langgraph/persistence
- LangGraph interrupts and human-in-the-loop: https://docs.langchain.com/oss/python/langgraph/interrupts
- LangChain tools: https://docs.langchain.com/oss/python/langchain/tools
- LangSmith observability: https://docs.smith.langchain.com/
- Pydantic documentation: https://docs.pydantic.dev/

Check current documentation for API changes before using the examples in production. The code in this manual is designed for teaching; mock integrations and in-memory persistence must be replaced with secure, durable implementations for real workloads.
