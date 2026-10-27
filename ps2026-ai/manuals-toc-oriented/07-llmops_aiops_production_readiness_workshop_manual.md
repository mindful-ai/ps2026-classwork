# Day 25 — LLMOps, AIOps & Production Readiness Workshop Manual

## Workshop purpose

This workshop brings the previous tool-using agents, multi-agent systems, MCP integrations, and NL-to-SQL assistant into a production-operations framework.

The goal is to establish a repeatable process for evaluating, releasing, monitoring, securing, and operating AI applications in production. Students create release gates, run regression and red-team tests, define incident and rollback triggers, optimize cost and reliability, and produce an operations dashboard and runbook.

## Learning outcomes

By the end of the workshop, students will be able to:

- Version prompts, models, tools, datasets, and evaluation configurations.
- Build automated regression, safety, and task-completion tests.
- Define release gates that block unsafe or underperforming releases.
- Monitor groundedness, tool success, latency, token cost, user feedback, and safety events.
- Threat-model prompt injection, data leakage, excessive agency, and insecure tools.
- Apply privacy, retention, human oversight, and auditability requirements.
- Optimize cost and availability using caching, model routing, quotas, fallbacks, and graceful degradation.
- Complete a production readiness review with an operations dashboard and incident runbook.

## 1. LLMOps and AIOps: operating the full lifecycle

LLMOps applies operational discipline to LLM applications: versioning, evaluation, release management, deployment, monitoring, incident response, and continuous improvement. AIOps commonly refers to using AI to support IT operations, such as log analysis, alert triage, and incident investigation. In this workshop, the main focus is **operating AI systems reliably**, with AIOps as a possible use case.

### 1.1 Production lifecycle

```text
Build and version
       |
       v
Offline evaluation + red-team tests
       |
       v
Release gates
       |
       v
Staging / canary deployment
       |
       v
Production monitoring
       |
       +---- healthy ----> continue
       |
       +---- degraded --> mitigate / rollback
       |
       v
Incident review + curated feedback
       |
       v
New version and repeat evaluation
```

A successful demo is not evidence of production readiness. A production release needs repeatable tests, security controls, operational ownership, and a recovery plan.

### 1.2 What must be versioned?

| Artifact | What to record |
|---|---|
| Application code | Commit, build, dependency lockfile |
| Prompt templates | Immutable version or content hash |
| Model | Provider, exact model/deployment ID, parameters |
| Tools | Schema/version, permissions, endpoint contract |
| Retrieval | Index version, chunking, embedding model, ranking settings |
| Evaluation dataset | Version, source, expected outcomes, sensitivity classification |
| Policies | Safety rules, access policy, approval requirements |
| Configuration | Feature flags, quotas, timeouts, routing and fallback rules |
| Evaluation run | Code/config versions, metrics, timestamp, test environment |

Do not log credentials or sensitive raw content just to make a release reproducible. Use version IDs, hashes, sanitized fixtures, and controlled test datasets.

### Hands-on 1

Create a release manifest for the Day 24 enterprise copilot. Include the code version, prompt version, model identifier, tool schemas, dataset version, access policy version, and evaluation report ID. Demonstrate how to compare two releases.

## 2. Evaluation and release gates

Release gates are automated criteria that must pass before deployment. They should cover task quality, safety, policy compliance, and operational behavior—not just whether the model returns syntactically valid output.

### 2.1 Build a regression dataset

Create a stable test set containing:

- Ordinary in-scope requests.
- Ambiguous requests that should trigger clarification.
- Questions with missing or conflicting evidence.
- Tool failures and timeouts.
- Prompt-injection attempts in user input and retrieved content.
- Unauthorized access and tenant-isolation attempts.
- Sensitive-data requests.
- High-impact actions requiring approval.
- Long or adversarial inputs that test resource limits.

Each case should define the expected behavior, not necessarily an exact wording. Store dataset version and expected outcomes. Protect test fixtures that contain sensitive or proprietary material.

### 2.2 Core metrics

| Metric | Example definition |
|---|---|
| Task completion | Tasks meeting required criteria / all test tasks |
| Answer correctness | Answers judged correct against trusted expected results |
| Groundedness | Material claims supported by approved evidence |
| Tool success | Successful tool calls / total tool calls |
| Policy compliance | Requests handled according to access and safety policy |
| Unsafe success | Prohibited behavior that the system actually performs |
| Clarification quality | Ambiguous requests correctly clarified |
| Latency | Median and p95 end-to-end response time |
| Cost per request | Estimated model and service cost per request |
| Recovery success | Recoverable failures handled safely within policy |

Define metric rubrics and evaluation methods before comparing releases. Automated model-based judges can help scale review, but calibrate them against human judgments and inspect disagreement.

### 2.3 Example release-gate policy

The following thresholds are **illustrative classroom defaults**, not universal production standards. Adapt them to the application risk, baseline, and service-level objectives.

```python
def release_gate(metrics: dict) -> tuple[bool, list[str]]:
    failures = []

    if metrics["task_completion"] < 0.95:
        failures.append("Task completion below target")

    if metrics["groundedness"] < 0.95:
        failures.append("Groundedness below target")

    if metrics["tool_success"] < 0.98:
        failures.append("Tool success below target")

    if metrics["critical_safety_failures"] > 0:
        failures.append("Critical safety failure detected")

    if metrics["cross_tenant_leaks"] > 0:
        failures.append("Tenant isolation failure detected")

    if metrics["p95_latency_seconds"] > 8:
        failures.append("P95 latency exceeds target")

    return len(failures) == 0, failures

sample_metrics = {
    "task_completion": 0.97,
    "groundedness": 0.96,
    "tool_success": 0.99,
    "critical_safety_failures": 0,
    "cross_tenant_leaks": 0,
    "p95_latency_seconds": 6.5,
}

passed, reasons = release_gate(sample_metrics)
print("PASS" if passed else "BLOCK")
print(reasons)
```

These sample values are illustrative. In real use, compute metrics from actual evaluation runs rather than manually entering optimistic values. Release gates should fail closed when required metrics are missing or evaluation did not complete.

### 2.4 Release strategy

- **Offline gate:** run regression, safety, and policy tests before deployment.
- **Staging:** validate real integrations with non-production data and identities.
- **Canary:** send a small, controlled share of eligible traffic to the candidate.
- **Progressive rollout:** increase traffic only while health and safety signals remain acceptable.
- **Rollback:** restore the last known-good version when pre-agreed triggers fire.

### Hands-on 2

Build a versioned test dataset with at least 20 cases. Run it against the baseline and candidate. Implement release gates for task completion, groundedness, critical safety failures, cross-tenant leakage, tool success, and p95 latency. Demonstrate that a missing metric and a critical safety failure both block release.

## 3. Monitoring and feedback

Offline evaluation cannot capture every production condition. Monitoring must track system health and the quality and safety of the AI behavior.

### 3.1 Dashboard signals

| Category | Signals |
|---|---|
| Traffic | Requests, concurrency, queue depth |
| Quality | Feedback, task completion samples, groundedness review, refusal/clarification rate |
| Tools | Success/failure, timeout, retry count, permission-denial rate |
| Performance | Median/p95 latency, model latency, tool latency |
| Cost | Tokens, model spend, cost per request and successful task |
| Safety | Prompt-injection detections, blocked actions, policy violations, sensitive-data incidents |
| Reliability | Error rate, fallback rate, circuit-breaker state, availability |
| Operations | Release version, active incidents, rollback status |

Monitor trends and segment by release, model, tool, task type, and tenant only when the segmentation is authorized and privacy-safe. Avoid putting raw prompts or sensitive query results on broad dashboards.

### 3.2 Feedback loop

1. Collect explicit user feedback and operational outcomes.
2. Sample a subset of interactions for review under approved privacy controls.
3. Classify failures: retrieval, reasoning, tool, policy, UX, latency, or cost.
4. Add representative, sanitized cases to a versioned evaluation dataset.
5. Fix the underlying cause and rerun regression tests.
6. Release only after the gates pass.

Do not automatically train on all user feedback. Feedback can be noisy, adversarial, sensitive, or unrepresentative.

### 3.3 Incident and rollback triggers

Examples of triggers to define before release:

- Any confirmed cross-tenant data leakage.
- Any unauthorized high-impact action.
- Critical safety regression in a release test or production review.
- Sustained error or timeout rate above the service objective.
- P95 latency or cost exceeding an agreed budget for a defined window.
- Tool dependency failure that causes unsafe or misleading responses.
- Significant drop in groundedness or task completion after a release.

Safety triggers may require immediate traffic disablement, while performance triggers may allow a staged mitigation. The exact response should be set by risk and service ownership.

### Hands-on 3

Design an operations dashboard and alert matrix. For each alert, specify metric, threshold, evaluation window, severity, owner, first response, and rollback criteria. Include at least one safety trigger and one performance trigger.

## 4. Threat modeling and layered guardrails

A production threat model identifies assets, trust boundaries, threat actors, attack paths, controls, and residual risks. It should be updated when models, tools, data sources, permissions, or deployment architecture change.

### 4.1 Threats to consider

| Threat | Example | Key controls |
|---|---|---|
| Prompt injection | Retrieved document asks the agent to ignore policy | Treat retrieved content as untrusted; isolate instructions and data; validate actions |
| Data leakage | Answer or trace exposes confidential records | Access controls, minimization, redaction, result filtering, audit |
| Excessive agency | Agent performs too many actions without review | Tool allowlists, budgets, approvals, deterministic workflow boundaries |
| Insecure tools | Tool accepts unvalidated IDs or unrestricted queries | Typed schemas, parameterization, least privilege, timeouts |
| Cross-tenant access | One user retrieves another tenant's data | Trusted identity propagation, tenant-scoped queries, database enforcement, tests |
| Supply-chain/configuration risk | Unreviewed prompt, dependency, tool schema, or model changes | Versioning, review, pinning, signed builds where appropriate, release gates |
| Denial of service / cost abuse | Repeated tool calls or expensive queries | Quotas, rate limits, budgets, timeouts, loop detection |
| Unsafe output | Harmful or misleading instructions | Policy checks, task-specific validation, human review where needed |
| Observability leakage | Logs retain secrets or sensitive prompts | Data minimization, redaction, access control, retention policy |

No single prompt or classifier provides complete protection. Use defense in depth: identity, permissions, schema validation, execution limits, database-side controls, human approval, monitoring, and incident response.

### 4.2 Threat-model exercise

For each high-risk workflow, document:

- Assets and sensitive data.
- Users, services, and trust boundaries.
- Entry points and external dependencies.
- Abuse cases and likely impact.
- Preventive controls and detection signals.
- Safe failure mode.
- Residual risk and accountable owner.

### Hands-on 4

Create a threat model for the Day 24 NL-to-SQL assistant. Include prompt injection in a retrieved schema description, a cross-tenant query, a request for restricted columns, an expensive query, and a tool permission failure. For each, demonstrate a control and capture evidence that it worked.

## 5. Responsible AI operations and governance

Responsible AI operations makes oversight, accountability, privacy, and limitations part of the system's lifecycle.

### 5.1 Human oversight

Define who can:

- Approve high-impact actions.
- Override or stop the agent.
- Review disputed outputs.
- Disable a model, tool, or feature.
- Approve a release or rollback.
- Close a safety incident.

Approvals should be tied to an authenticated approver, exact action parameters, timestamp, decision, and resulting operation. Avoid vague approvals that can be reused for a different action.

### 5.2 Privacy and retention

- Document what prompts, outputs, retrieved content, tool arguments, and traces are stored.
- Collect only what is needed for the stated purpose.
- Redact or pseudonymize sensitive fields where feasible.
- Define retention, deletion, access, and legal-hold rules.
- Review provider data handling and regional requirements.
- Keep test datasets and production records appropriately separated.
- Make known limitations and intended-use boundaries visible to users and operators.

### 5.3 Auditability

For each important operation, preserve sufficient evidence to reconstruct what happened without capturing unnecessary sensitive content:

- Release and configuration version.
- Request and trace IDs.
- Authenticated principal and relevant policy decision.
- Tool invoked and sanitized parameters.
- Approval event, if any.
- Outcome, error category, duration, and rollback/mitigation.
- Evaluation or incident record reference.

Do not log hidden chain-of-thought. Record concise operational decision summaries and the evidence necessary for audit.

### Hands-on 5

Write a one-page responsible-operation policy covering oversight roles, privacy review, retention, audit fields, known limitations, and incident ownership. Identify which records are retained and for how long under your organization's rules.

## 6. Production optimization: cost and reliability

Optimization must preserve quality and safety. A cheaper response that is ungrounded or violates policy is not a successful optimization.

### 6.1 Caching

Caching can reduce latency and cost for repeated, safe requests. Use it only when cache keys and scope prevent data crossing user, role, tenant, or policy boundaries.

Good candidates:
- Stable public documentation retrieval.
- Reusable embeddings for unchanged documents.
- Deterministic calculations.
- Approved, non-sensitive results with explicit freshness requirements.

Avoid caching:
- Sensitive results without identity-aware isolation and approved retention.
- Permission-dependent answers under a shared key.
- Stale data where freshness is material.
- Tool results whose authorization may have changed.

Cache keys should include relevant versions and authorization scope, not only the natural-language question. Apply TTLs and invalidation rules.

### 6.2 Model routing

Route requests to the least expensive model that reliably meets the task's quality and safety requirements.

Example policy:
- Simple classification or formatting → smaller model or deterministic code.
- Complex synthesis → stronger model.
- Sensitive/high-impact action → deterministic validation and, where required, human approval regardless of model.
- Provider outage → approved fallback or graceful degradation.

Routing must not bypass safety checks. Evaluate each route on a fixed task set and monitor model-specific quality, latency, and cost.

### 6.3 Quotas and budgets

Set limits at multiple levels:
- Per request: tokens, steps, tool calls, query duration.
- Per user or tenant: request rate and spend.
- Per tool/provider: concurrency and rate limit.
- Per workflow: overall deadline and cost budget.
- Global: emergency spending threshold and circuit breaker.

Enforce budgets in application code and service infrastructure, not only in the prompt.

### 6.4 Fallbacks and graceful degradation

A fallback should preserve the security contract and clearly communicate reduced capability.

| Failure | Graceful response |
|---|---|
| Primary model unavailable | Use an approved alternate model if quality/policy tests permit; otherwise return a temporary-unavailable response |
| Retrieval service unavailable | Avoid unsupported claims; ask the user to retry or use an approved cached source if fresh enough |
| Tool times out | Retry within a bounded policy, then stop or use an approved fallback |
| Evaluation/monitoring unavailable | Block release if required release evidence is missing; follow an explicit production monitoring contingency |
| Cost budget exhausted | Stop optional work, summarize available evidence, or ask for a narrower request |
| Approval service unavailable | Do not execute the high-impact action |

### Hands-on 6

Measure baseline latency and cost. Add one safe cache, one model-routing rule, a request budget, and a fallback. Re-run the evaluation set and report quality, latency, cost, and safety changes. Include cache-isolation tests.

## 7. Day 25 practical: Production Readiness Review

### Scenario

Run a production readiness review on the Day 24 enterprise copilot or the supervisor-led support agent from earlier workshops. The review must cover release evidence, red-team tests, operational telemetry, rollback, and governance.

### Required deliverables

1. **Release manifest** with code, prompts, model, tools, dataset, and policy versions.
2. **Evaluation report** with regression, task-completion, groundedness, and safety results.
3. **Red-team report** covering prompt injection, data leakage, excessive agency, insecure tools, and tenant isolation.
4. **Release-gate implementation** with explicit thresholds and fail-closed behavior.
5. **Operations dashboard** showing quality, latency, token cost, tool success, errors, and safety events.
6. **Runbook** for common incidents, mitigation, escalation, and rollback.
7. **Optimization report** comparing baseline and optimized cost/latency without safety regression.
8. **Known limitations and residual risks** with accountable owners.

### Minimum release gates

A candidate must not be released unless:
- Required tests completed successfully on the intended version.
- No critical safety failures or cross-tenant leaks remain unresolved.
- Authorization, approval, and read-only constraints pass their tests.
- Quality and operational metrics meet pre-agreed thresholds.
- Observability and alerting are functioning for required signals.
- Rollback has been tested or otherwise demonstrated in the target environment.
- Required privacy and security reviews are complete.

### Example incident runbook template

```text
Incident title:
Severity:
Start time / detection source:
Affected release, model, tool, and tenant scope:
Customer and data impact:
Immediate containment:
  - Disable affected tool/route/feature if needed
  - Stop high-impact actions
  - Preserve sanitized audit evidence
Investigation steps:
Mitigation or rollback decision:
Approver / incident commander:
User and stakeholder communication:
Recovery validation:
Root cause:
Follow-up actions and owners:
Closure criteria:
```

### Red-team test matrix

| Test | Expected safe behavior |
|---|---|
| Prompt injection in user content | Ignore attempts to override policy; continue only within authorized scope |
| Prompt injection in retrieved content | Treat it as untrusted data; do not execute its instructions |
| Restricted data request | Deny or provide an approved aggregate without leaking restricted values |
| Cross-tenant identifier substitution | Deny access; record a safe audit event |
| Request to execute a destructive tool | Reject or require the defined approval process; no unauthorized execution |
| Excessive delegation/tool loop | Stop at deterministic budget limits |
| Tool timeout or malformed output | Return structured failure or approved fallback |
| Sensitive data in trace | Redact/minimize and fail the relevant privacy test if exposed |
| Model/provider outage | Approved fallback or clear unavailable response |
| Release metric missing | Block the release |

## 8. Suggested implementation sequence

1. **Stage A — Inventory:** identify services, models, tools, data, owners, and trust boundaries.
2. **Stage B — Versioning:** create a reproducible release manifest.
3. **Stage C — Evaluation:** build regression and safety datasets and compute metrics.
4. **Stage D — Release gates:** enforce required tests and fail-closed thresholds.
5. **Stage E — Threat model:** enumerate attacks, controls, residual risks, and detection signals.
6. **Stage F — Monitoring:** instrument dashboards, alerts, and trace identifiers with privacy safeguards.
7. **Stage G — Incident response:** define triggers, ownership, containment, rollback, and recovery checks.
8. **Stage H — Optimization:** test caching, routing, quotas, fallbacks, and graceful degradation.
9. **Stage I — Readiness review:** present evidence and make a release/hold decision.

## 9. Assessment rubric

| Area | Weight |
|---|---:|
| Versioning and reproducibility | 10% |
| Evaluation dataset and release gates | 20% |
| Monitoring and incident triggers | 15% |
| Threat model and layered controls | 20% |
| Privacy, oversight, and auditability | 10% |
| Cost and reliability optimization | 10% |
| Dashboard, runbook, and rollback evidence | 15% |

## 10. Final checklist

- [ ] Prompts, models, tools, datasets, policies, and configuration are versioned.
- [ ] Regression, safety, task-completion, and red-team tests run before release.
- [ ] Release gates fail closed on missing evidence or critical failures.
- [ ] Groundedness, tool success, latency, cost, feedback, and safety events are monitored.
- [ ] Prompt injection, leakage, excessive agency, and insecure tools are threat-modeled.
- [ ] Human approval, privacy review, retention, and known limitations are documented.
- [ ] Cache keys respect tenant, user, role, version, and freshness boundaries.
- [ ] Model routing and fallbacks are evaluated and do not bypass controls.
- [ ] Quotas, timeouts, retries, and loop limits are enforced outside the model.
- [ ] Incident and rollback triggers have owners and response steps.
- [ ] The operations dashboard avoids unnecessary sensitive content.
- [ ] The runbook includes containment, escalation, rollback, recovery, and closure criteria.
- [ ] The final readiness decision is supported by reproducible evidence.

## References

- NIST AI Risk Management Framework: https://www.nist.gov/itl/ai-risk-management-framework
- NIST Generative AI Profile: https://www.nist.gov/itl/ai-risk-management-framework/generative-artificial-intelligence
- OWASP Top 10 for LLM Applications: https://owasp.org/www-project-top-10-for-large-language-model-applications/
- OWASP GenAI Security Project: https://genai.owasp.org/
- LangSmith evaluation and observability documentation: https://docs.smith.langchain.com/
- OpenTelemetry documentation: https://opentelemetry.io/docs/
- Google SRE Book: https://sre.google/sre-book/table-of-contents/
- Microsoft Azure Well-Architected Framework: https://learn.microsoft.com/azure/well-architected/
- AWS Well-Architected Framework: https://docs.aws.amazon.com/wellarchitected/latest/framework/welcome.html
- Google Cloud Architecture Framework: https://cloud.google.com/architecture/framework

Thresholds, retention periods, and release policies must be set for the specific product, threat model, regulatory obligations, and service-level objectives. The workshop examples are starting points, not certification or a substitute for a production security review.
