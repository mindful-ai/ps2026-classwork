# Day 26 — Visual AI Workflows, Dynamic Agents & Human-in-the-Loop Workshop Manual

## Workshop purpose

This workshop explores the next stage of AI application development: combining visual, low-code workflow design with programmatic agent orchestration. Students build AI systems using Langflow, expose workflows as API endpoints, dynamically create agents within controlled boundaries, and design long-running agents with reusable skills, state, and human approval.

The emphasis is on **hybrid development**: visual tools for rapid prototyping and understandable workflow design, combined with Python for validation, integration, testing, and production controls.

## Learning outcomes

By the end of the workshop, students will be able to:

- Build AI workflows using Langflow components and connections.
- Compare Langflow with alternative visual AI development platforms.
- Expose a workflow or inference pipeline through an API endpoint.
- Integrate the endpoint into another Python application.
- Dynamically select or create agents within predefined safety boundaries.
- Design long-running agents using persistent state, reusable skills, and execution harnesses.
- Implement human-in-the-loop interruptions, approvals, and feedback-driven continuation.

## 1. Visual and hybrid AI development

Visual AI builders represent applications as connected components. They can accelerate prototyping, make data flow easier to inspect, and help teams collaborate. They do not remove the need to understand prompts, model behavior, data access, security, testing, or deployment.

### 1.1 A typical visual workflow

```text
Input
  |
  v
Prompt / validation
  |
  v
Model
  |
  v
Parser / output validation
  |
  v
Response
```

A retrieval-augmented workflow may add document loaders, chunking, embeddings, a vector store, retrieval, and grounded answer generation. An agentic workflow may add tool nodes, routing, state, approval steps, and bounded loops.

### 1.2 Langflow concepts

Langflow is a visual builder for assembling AI workflows from components. Component availability and UI details can change by release and installation.

Typical concepts include:

- **Components:** model, prompt, input, output, data loader, parser, vector store, tool, and custom Python component.
- **Connections:** pass data from one component to another.
- **Flow:** the connected workflow and its configuration.
- **Playground/testing:** experiment with inputs and inspect outputs.
- **API access:** expose a flow for use by external applications, depending on deployment and version.
- **Custom components:** wrap reusable Python functionality where the built-in components are insufficient.

### 1.3 Suggested first flow

Build a simple question-answer flow:

1. Input component receives a question.
2. Prompt template combines instructions and the question.
3. Chat model generates an answer.
4. Output component returns the response.
5. Test ordinary, ambiguous, and adversarial inputs.

Then extend it with structured output validation or retrieval from an approved knowledge source.

### Hands-on 1

Create a Langflow flow that accepts a question, applies a clear system instruction, invokes a model, and returns an answer. Test at least five inputs, record the model/configuration used, and export or document the flow so another student can reproduce it.

## 2. Alternatives to Langflow

Different tools optimize for different levels of visual design, orchestration, developer control, and deployment. Features and licensing may change, so verify current official documentation before choosing.

| Platform | General orientation | Evaluate it for |
|---|---|---|
| Langflow | Visual composition of LLM and data workflows | Fast prototyping, component connections, API serving |
| Flowise | Visual LLM, RAG, and agent flow builder | Node-based workflows and quick integration prototypes |
| Dify | Application platform for LLM apps and workflows | App lifecycle, workflow design, knowledge features, deployment |
| n8n | General workflow automation with AI integrations | Connecting business apps, events, and AI steps |
| LangGraph (code-first) | Explicit stateful graph orchestration | Fine-grained control, state, routing, checkpointing, and approvals |
| Semantic Kernel | SDK for AI orchestration and enterprise integrations | Application-centric orchestration and plugin/function integration |

### Selection criteria

Compare platforms using:

- Ability to export, version, and review workflows.
- API and authentication support.
- Custom code and tool integration.
- Stateful execution, checkpoints, and human approval.
- Observability, testing, and evaluation.
- Deployment model, data residency, and access controls.
- Team skills, maintainability, and total operating cost.

Visual workflows and code-first frameworks can coexist. A visual prototype may establish the desired behavior; a code-first implementation may be preferable when complex state transitions, tests, security controls, or production review require more explicit control.

### Hands-on 2

Compare Langflow with one alternative for the same simple question-answer flow. Record setup effort, model integration, API exposure, versioning, access control, and testability. Explain which one you would choose for a classroom prototype and for a regulated production application.

## 3. Exposing a workflow as an endpoint

A workflow becomes more reusable when another application can invoke it through a stable API. Endpoint availability, paths, authentication mechanisms, and request schemas depend on the installed Langflow version and deployment configuration; use the UI and current documentation to obtain the actual endpoint and request format.

### 3.1 Endpoint design checklist

Before exposing a flow, define:

- Request and response schema.
- Authentication and authorization.
- Request size and rate limits.
- Timeouts and concurrency limits.
- Model/tool budgets.
- Error response format.
- Logging and trace IDs.
- Data handling and retention.
- Versioning and compatibility expectations.

Do not expose an unauthenticated development server directly to the public internet. Use an approved gateway or authenticated deployment, TLS, and least-privilege service credentials.

### 3.2 Example client pattern

The following generic Python example illustrates the client-side pattern. Replace the endpoint, headers, and payload with the exact values provided by your deployed Langflow instance; these are placeholders, not a guaranteed Langflow API schema.

```python
import os
import requests

FLOW_ENDPOINT = os.environ["AI_FLOW_ENDPOINT"]
FLOW_API_KEY = os.environ["AI_FLOW_API_KEY"]

def invoke_flow(question: str) -> dict:
    response = requests.post(
        FLOW_ENDPOINT,
        headers={
            "Authorization": f"Bearer {FLOW_API_KEY}",
            "Content-Type": "application/json",
        },
        json={
            # Replace this payload with the schema for your deployed flow.
            "input_value": question,
        },
        timeout=30,
    )

    response.raise_for_status()
    return response.json()

# Example usage after setting the endpoint and key:
# result = invoke_flow("Summarize the approved incident report.")
# print(result)
```

This is an illustrative integration pattern. Do not assume every Langflow deployment uses this authentication header or body structure. Follow the endpoint documentation for your version and deployment.

### 3.3 Integrate the endpoint into another project

A calling application should wrap the API in a small adapter that:

- Validates the caller's input.
- Keeps endpoint credentials server-side.
- Enforces timeouts and safe error handling.
- Normalizes the response to an internal schema.
- Records a request/trace ID.
- Handles retries only for suitable transient errors.
- Avoids logging secrets or sensitive payloads.

### Hands-on 3

Expose the Langflow question-answer flow through its supported API. Call it from a separate Python script. Test a valid request, invalid input, timeout or simulated server error, and missing credentials. Document the real request/response schema and authentication mechanism used in your environment.

## 4. Spawning agents dynamically

Dynamic agent spawning means selecting, configuring, or instantiating an agent at runtime based on a task. It does **not** mean allowing a model to create unlimited agents, invent tools, or bypass application policies.

### 4.1 Safe design

1. Define a finite registry of approved agent roles.
2. Give each role a schema, allowed tools, budget, and output contract.
3. Let a planner propose which registered role is needed.
4. Validate the proposal in application code.
5. Instantiate only approved roles.
6. Enforce limits on agent count, depth, tool calls, time, and cost.
7. Collect typed results and let the supervisor decide whether to continue.

Example role registry:

```python
AGENT_REGISTRY = {
    "researcher": {
        "allowed_tools": ["search_approved_docs"],
        "max_tool_calls": 4,
    },
    "reviewer": {
        "allowed_tools": ["check_claim_support"],
        "max_tool_calls": 3,
    },
    "summarizer": {
        "allowed_tools": [],
        "max_tool_calls": 0,
    },
}

MAX_AGENTS_PER_TASK = 3

def validate_agent_plan(proposed_roles: list[str]) -> list[str]:
    if len(proposed_roles) > MAX_AGENTS_PER_TASK:
        raise ValueError("Agent budget exceeded")

    unknown = [
        role for role in proposed_roles
        if role not in AGENT_REGISTRY
    ]
    if unknown:
        raise ValueError(f"Unapproved agent role(s): {unknown}")

    # Preserve order while removing duplicates.
    return list(dict.fromkeys(proposed_roles))

print(validate_agent_plan(["researcher", "reviewer"]))
```

The registry is only a policy input. Actual tool permissions must also be enforced by the tool layer; a role description or Python dictionary alone is not a security boundary.

### 4.2 When dynamic spawning is useful

- Requests contain independent subproblems that can be delegated.
- A task needs a specialist only under certain conditions.
- A reviewer is needed for high-risk or low-confidence results.
- The system needs to adapt the plan while staying within a fixed capability set.

Avoid spawning agents for straightforward deterministic tasks or when the coordination cost exceeds the benefit.

### Hands-on 4

Build a small agent registry with researcher, reviewer, and summarizer roles. Implement role validation, maximum agent count, tool allowlists, and typed results. Test unknown roles, duplicate roles, and budget exhaustion.

## 5. Deep Agents and long-running work

“Deep Agents” can refer to agent systems designed for complex, multi-step tasks that benefit from planning, delegation, persistent state, and reusable capabilities. Specific frameworks and libraries may use the term differently; the architecture principles in this chapter apply regardless of implementation.

Long-running agents need more than a large context window. They need explicit task state, durable checkpoints, resumability, budgets, progress reporting, and safe handling of interruption.

### 5.1 Long-running agent architecture

```text
User goal
   |
   v
Plan + acceptance criteria
   |
   v
Bounded task queue
   |
   v
Execute skill / tool
   |
   v
Checkpoint state + record evidence
   |
   v
Evaluate progress
   |                  |
   | continue         | complete / blocked
   v                  v
Next bounded task   Report / escalate
```

### 5.2 Reusable skills and harness

A **skill** is a reusable capability with a clear input/output contract. A **harness** is the shared runtime that enforces limits, validation, permissions, tracing, recovery, and approval.

Example skills:
- `search_approved_docs(query)`
- `summarize_evidence(items)`
- `validate_claims(answer, evidence)`
- `create_report(findings)`
- `request_approval(action)`

Harness responsibilities:
- Validate every input and output.
- Enforce tool allowlists and user/tenant permissions.
- Apply step, time, cost, and tool-call budgets.
- Store checkpoints and task status securely.
- Track completed operations to avoid duplicate side effects.
- Normalize errors and implement bounded retries.
- Provide progress and cancellation controls.
- Emit privacy-conscious operational telemetry.

### 5.3 State and checkpointing

Persist the minimum information required to resume:

```python
long_running_state = {
    "task_id": "research-001",
    "goal": "Prepare an evidence-backed incident report",
    "plan": ["collect evidence", "validate claims", "write report"],
    "completed_steps": [],
    "findings": [],
    "errors": [],
    "pending_approval": None,
    "step_count": 0,
    "status": "running",
}
```

For a real implementation, use a durable, access-controlled persistence layer. Include schema/version information and retention rules. A checkpoint should not automatically be treated as trusted: validate it when loading, and scope it to the correct user or tenant.

### Hands-on 5

Extend a prior LangGraph workflow to process a multi-step research task. Add a persistent checkpoint, progress status, bounded execution, cancellation, and safe resume. Demonstrate that resuming does not repeat a completed external side effect.

## 6. Human-in-the-loop (HITL)

Human-in-the-loop workflows pause execution when the system needs approval, clarification, review, or correction. Human feedback should be incorporated through explicit state transitions rather than being appended informally to a prompt.

### 6.1 Common interruption points

- Missing or ambiguous requirements.
- Conflicting evidence that changes the conclusion.
- Sensitive or consequential actions.
- Low confidence or policy uncertainty.
- A proposed external communication or data modification.
- A review checkpoint before a deliverable is published.

### 6.2 Approval workflow

```text
Agent prepares proposed action
           |
           v
Validate action + permissions
           |
           v
Pause and present exact parameters
           |
           v
Human approves / rejects / edits
           |
           v
Revalidate changed parameters
           |
           v
Execute approved action or stop
           |
           v
Record decision and outcome
```

Approval should be authenticated and bound to the exact action, scope, and parameters. If the action changes after approval, request approval again. A human approval mechanism does not replace authorization checks.

### 6.3 LangGraph interruption pattern

LangGraph supports pausing graph execution for human input using its interrupt/checkpoint mechanisms. Exact APIs and requirements can change; check the current documentation for the installed version. A conceptual node may look like:

```python
# Conceptual pattern: integrate with a compiled LangGraph graph
# and a configured checkpointer. Verify the current API for your version.

from langgraph.types import interrupt

def approval_node(state):
    decision = interrupt({
        "kind": "approval_required",
        "action": state["pending_action"],
        "message": "Review the proposed action and its parameters."
    })

    if decision.get("approved") is True:
        return {"approval_status": "approved"}

    return {"approval_status": "rejected"}
```

This snippet illustrates the intent, not a complete runnable graph. A full exercise must compile the graph with a suitable checkpointer, invoke it with a stable thread ID, handle the interrupt response using the documented resume API, and revalidate the action before execution.

### 6.4 Incorporating human feedback

Store structured feedback such as:

- Decision: approve, reject, request clarification, or revise.
- Reason category.
- Corrected facts or constraints.
- Approver identity and timestamp, where appropriate.
- Version of the pending action and workflow.
- Result of resuming execution.

Use feedback for the current task immediately when authorized. Incorporate it into future prompts, skills, or evaluation data only through a reviewed change process; do not automatically turn all feedback into durable memory or training data.

### Hands-on 6

Add an approval interruption before a mock ticket update. Test approval, rejection, edited parameters, repeated resume, and missing approver identity. Verify that the action executes only once and only after approval of the exact parameters.

## 7. Day 26 practical: Hybrid AI Workflow and Long-Running Agent

### Scenario

Build a visual workflow that researches a support issue and produces a concise report. Expose the workflow through an API. A Python client invokes it. For more complex requests, a bounded supervisor selects registered agents or skills. The workflow pauses for human review before publishing or performing a consequential action.

### Required architecture

```text
Client application
      |
      v
Authenticated workflow endpoint
      |
      v
Input validation + policy
      |
      v
Visual flow (Langflow)
      |
      v
Bounded orchestration / registered skills
      |
      v
Evidence validation
      |
      +------> Human approval if needed
      |
      v
Final response + audit record
```

### Required controls

- Documented flow version and API contract.
- Authenticated endpoint with server-side secret management.
- Input validation, timeouts, rate limits, and safe errors.
- Approved agent registry and tool allowlists.
- Agent-count, step, tool-call, time, and cost budgets.
- Checkpointing and safe resume for long-running work.
- Human approval for consequential actions.
- Approval bound to exact parameters and authenticated reviewer.
- Trace IDs and privacy-conscious logging.
- Tests for success, failures, interruption, and recovery.

### Test matrix

| Test | Expected behavior |
|---|---|
| Valid API request | Returns a validated response |
| Missing or invalid credentials | Request is denied |
| Unknown agent role proposed | Plan is rejected safely |
| Agent budget exceeded | Workflow stops or requests a smaller plan |
| Tool timeout | Bounded retry or controlled fallback |
| Long-running task interrupted | State is checkpointed and can resume |
| Approval rejected | Consequential action is not executed |
| Approved action modified | New approval is required |
| Duplicate resume or retry | No duplicate external side effect |
| Sensitive value in logs | Redaction/minimization policy is applied |

### Capstone deliverables

1. Exported or documented Langflow flow and version information.
2. API endpoint contract and a Python client integration.
3. Agent/skill registry and harness policy.
4. Long-running workflow with checkpoint and resume.
5. Human approval path with approval/rejection tests.
6. Test report covering security, reliability, and failure behavior.
7. Architecture diagram and short deployment guide.

## 8. Suggested implementation sequence

1. **Stage A — Visual prototype:** build and test a simple Langflow flow.
2. **Stage B — Alternatives:** compare one visual platform and one code-first approach.
3. **Stage C — API exposure:** publish the flow using the supported deployment endpoint and call it from Python.
4. **Stage D — Harness:** add input validation, tool permissions, budgets, and safe errors.
5. **Stage E — Dynamic roles:** add a finite registry and validated agent selection.
6. **Stage F — Long-running state:** add checkpoints, progress, cancellation, and resume.
7. **Stage G — HITL:** pause for approval and safely resume after a human decision.
8. **Stage H — Evaluation:** test success, security boundaries, timeouts, and repeated execution.

## 9. Assessment rubric

| Area | Weight |
|---|---:|
| Visual workflow design and reproducibility | 15% |
| API exposure and client integration | 15% |
| Dynamic agent selection and bounded roles | 15% |
| Skills and harness controls | 15% |
| Long-running state and resumability | 15% |
| HITL interruption and feedback handling | 15% |
| Testing, documentation, and safe failure | 10% |

## 10. Final checklist

- [ ] The visual flow is versioned and reproducible.
- [ ] Platform selection is justified by requirements, not novelty.
- [ ] The API schema and authentication mechanism are documented.
- [ ] Endpoint secrets are stored outside prompts and source code.
- [ ] Inputs, outputs, timeouts, and errors are validated.
- [ ] Dynamic agents come from an approved registry.
- [ ] Tool permissions and execution budgets are enforced outside the model.
- [ ] Long-running tasks persist minimal, scoped, validated state.
- [ ] Resume behavior does not duplicate side effects.
- [ ] Human approval is authenticated and action-specific.
- [ ] Feedback is structured and does not silently become permanent memory.
- [ ] Logs are useful for operations without retaining unnecessary sensitive data.
- [ ] Failure, rejection, timeout, and recovery paths are tested.

## References

- Langflow documentation: https://docs.langflow.org/
- Langflow API documentation: https://docs.langflow.org/api
- Flowise documentation: https://docs.flowiseai.com/
- Dify documentation: https://docs.dify.ai/
- n8n documentation: https://docs.n8n.io/
- LangGraph overview: https://docs.langchain.com/oss/python/langgraph/overview
- LangGraph persistence: https://docs.langchain.com/oss/python/langgraph/persistence
- LangGraph interrupts: https://docs.langchain.com/oss/python/langgraph/interrupts
- Pydantic documentation: https://docs.pydantic.dev/

Verify the current official documentation for API paths, authentication, component availability, and interrupt/resume APIs before implementation. The examples are teaching patterns; production deployment requires environment-specific security, persistence, monitoring, and evaluation.
