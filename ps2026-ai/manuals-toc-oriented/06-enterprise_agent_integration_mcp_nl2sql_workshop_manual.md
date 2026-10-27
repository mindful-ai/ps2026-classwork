# Day 24 — Enterprise Agent Integration Workshop Manual

## Workshop purpose

This workshop moves from multi-agent coordination to secure integration with enterprise systems and data. Students learn how agents discover capabilities through the Model Context Protocol (MCP), how to enforce enterprise access controls, and how to build a natural-language-to-SQL (NL-to-SQL) assistant that queries business data safely.

The central security principle is: **model-generated actions are untrusted proposals**. Application policy, identity, tool validation, and database permissions determine what actually executes.

## Learning outcomes

By the end of the workshop, students will be able to:

- Explain MCP clients, servers, tools, resources, and capability discovery.
- Compare MCP-based integration with direct API calls.
- Apply authentication, authorization, tenant isolation, secrets management, and audit logging.
- Build an NL-to-SQL pipeline with schema retrieval, semantic disambiguation, SQL validation, and controlled execution.
- Enforce read-only access, allow-listed data sources, query limits, RBAC, and row/column restrictions.
- Map agent, model, and search services across Azure, AWS, and Google Cloud while keeping orchestration and evaluation portable.
- Build a secure enterprise copilot and demonstrate safe failure behavior.

## 1. MCP fundamentals

The Model Context Protocol (MCP) is a protocol for exposing tools and contextual resources to AI applications through a standardized client-server interaction. It helps separate the application or agent from the systems that provide capabilities.

### 1.1 Main components

| Component | Responsibility | Example |
|---|---|---|
| MCP host/application | The AI application that coordinates model interaction and MCP connections | An enterprise copilot |
| MCP client | Maintains a protocol connection to an MCP server | Client embedded in the copilot |
| MCP server | Exposes capabilities under defined contracts | Approved data-query server |
| Tool | An invokable operation with a schema | `search_orders` |
| Resource | Context/data exposed for the client to retrieve | A read-only schema description |
| Prompt (where supported) | A reusable prompt template exposed by a server | A standard incident-investigation prompt |

A server advertises capabilities, and clients can discover available tools and their input schemas. Discovery tells the client what is available; it does **not** prove the caller is authorized to perform every action. Authorization must be enforced at the server and underlying system.

### 1.2 Typical MCP interaction

```text
Enterprise copilot (host)
    |
    v
MCP client
    |  initialize / negotiate capabilities
    |  discover tools and resources
    v
MCP server
    |
    v
Authenticated enterprise service
    |
    v
Policy checks + audit + result
```

The server should expose a small, intentional capability surface rather than a generic “execute anything” tool.

### 1.3 MCP versus direct API integration

| Consideration | MCP integration | Direct API integration |
|---|---|---|
| Interface | Standardized protocol and capability discovery | Provider-specific endpoint and client |
| Tool discovery | Can enumerate server-provided tools and schemas | Usually coded or configured by the application |
| Interoperability | Helpful when multiple compatible clients consume the same server | Strong for a tightly controlled application/provider pairing |
| Control | Server still needs authorization, validation, and limits | Application/API gateway can enforce the same controls |
| Operational overhead | Adds a protocol server, connection, and lifecycle to manage | May be simpler for a small number of stable endpoints |
| Best fit | Reusable capabilities across AI applications | Direct, well-defined integration with a known service |

MCP is not inherently more secure than a direct API. Choose it when standardized discovery and reuse provide value. A direct API can be the better choice for a narrow integration with strict, well-understood requirements.

### Hands-on 1

Draw an MCP architecture for a support copilot that can search approved documents and retrieve ticket status. Identify the host, client, server, tools, resources, identity context, and authorization enforcement point. Explain what you would gain or lose by calling the ticket API directly.

## 2. Secure enterprise connectivity

A tool schema is not an access-control policy. Security must be enforced across identity, transport, application, and data layers.

### 2.1 Authentication and authorization

- **Authentication:** establish which user, service, or workload is making the request.
- **Authorization:** determine what that identity may read or do, on which resource, under which conditions.
- **Tenant isolation:** ensure one tenant cannot access another tenant's data through parameters, cached results, memory, traces, or shared connections.
- **Delegation:** pass user identity or a securely scoped delegated token where required; do not blindly use an overprivileged service identity for all users.
- **Revalidation:** recheck authorization at execution time, not just when the tool was discovered.

Use the identity and authorization mechanisms supported by the actual enterprise environment. Do not treat a user ID supplied in model-generated JSON as proof of identity.

### 2.2 Secrets management

- Store API keys, database credentials, and signing secrets in a secret manager or secure runtime configuration.
- Never place secrets in prompts, model-visible tool descriptions, source control, test fixtures, or trace payloads.
- Use short-lived credentials where practical and rotate them under organizational policy.
- Grant separate credentials to development, test, and production.
- Prefer workload identity or managed identity where supported.

### 2.3 Audit evidence

An audit event should capture operational facts such as:

- Request, trace, tenant, and authenticated principal identifiers, using approved pseudonymous identifiers where appropriate.
- Tool or operation name.
- Data source and policy decision.
- Validated operation category and safe parameter summary.
- Approval record, where applicable.
- Start/end time, duration, outcome, and sanitized error category.

Avoid logging passwords, access tokens, complete sensitive result sets, or unnecessary personal data. Define log access, integrity protection, and retention rules.

### 2.4 High-impact actions and approval

For consequential actions, separate proposal from execution:

1. The model proposes an action.
2. The application validates the schema and checks the user's authority.
3. A policy layer classifies the impact.
4. If required, an authorized human approves the exact action and parameters.
5. The system revalidates authorization and executes.
6. The outcome and approval are recorded.

If the action or parameters change after approval, request approval again. Do not rely on prompt instructions alone to prevent sensitive actions.

### Hands-on 2

Create a security matrix for a read-only document search, ticket lookup, and ticket update. For each operation, define authentication, authorization, tenant boundary, secrets handling, audit fields, and whether approval is required.

## 3. NL-to-SQL architecture

NL-to-SQL converts a user's natural-language question into a query over an authorized data source. It should be treated as a controlled data-access pipeline, not as a model that receives unrestricted database access.

### 3.1 Recommended architecture

```text
User question + authenticated identity
              |
              v
Intent and permission checks
              |
              v
Schema retrieval + business glossary
              |
              v
Semantic disambiguation
              |
              v
SQL generation (model proposes SQL)
              |
              v
SQL parsing and policy validation
              |
              v
Read-only database identity + query limits
              |
              v
Result minimization and output checks
              |
              v
Answer with query/evidence metadata
```

The database account and database-side policies are critical safeguards. An application validator is useful but should not be the only barrier protecting data.

### 3.2 Schema retrieval

Do not send the entire enterprise schema to the model by default. Retrieve only the relevant, authorized schema details for the task:

- Allowed table and view names.
- Column names and safe descriptions.
- Relationships and join keys.
- Data types and time semantics.
- Approved measures and dimensions.
- Business glossary terms and metric definitions.
- Sensitivity labels and restrictions.

Schema retrieval itself must respect user permissions. Hidden tables or columns should not be revealed just because the model asks for them.

### 3.3 Semantic disambiguation

Business language is often ambiguous. “Revenue,” “active customer,” “last month,” and “top product” can each have multiple definitions.

Before generating SQL, the assistant should:

1. Identify the requested measure, dimensions, filters, and time range.
2. Match terms to approved business definitions.
3. Ask a clarifying question when materially different interpretations remain.
4. State important assumptions in the response.
5. Use approved metric definitions rather than inventing calculations.

Example: “sales last quarter” may mean booked revenue, recognized revenue, or order value. If the organization's glossary does not resolve this, the assistant should ask.

### Hands-on 3

Create a small business glossary for `revenue`, `active customer`, and `last quarter`. Include a definition, source table/view, calculation, time basis, and owner. Test questions that intentionally use ambiguous wording.

## 4. SQL generation, validation, and read-only execution

The model must never have a general-purpose database credential or an unrestricted execution path.

### 4.1 Generate SQL as a proposal

Ask the model to return structured fields such as:

- `sql`: proposed query.
- `tables`: expected tables/views.
- `assumptions`: semantic assumptions.
- `needs_clarification`: whether the request is ambiguous.

Validate the response against a schema, then parse and validate the SQL before execution. Do not rely on a prompt saying “only generate safe SQL.”

### 4.2 Defense-in-depth validation

A robust design should:

1. Use a SQL parser or a carefully chosen query builder, not only string matching.
2. Permit only the expected statement type (typically a single `SELECT`, possibly a tightly controlled read-only CTE).
3. Reject multiple statements and DDL/DML operations such as `DROP`, `ALTER`, `DELETE`, `UPDATE`, `INSERT`, `CREATE`, and `TRUNCATE`.
4. Resolve referenced tables and columns against an allowlist and the user's permissions.
5. Reject unauthorized joins, functions, schemas, and external access features.
6. Enforce parameterized values where the database driver supports them.
7. Add a maximum row limit and statement timeout.
8. Execute using a read-only database principal with least privilege.
9. Enforce row-level and column-level controls in the database or trusted data-access layer.
10. Limit returned data and redact or aggregate sensitive values where required.

A string search for keywords is not a sufficient SQL security validator: keywords can appear in comments, identifiers, nested expressions, or dialect-specific constructs. Use a dialect-aware parser and enforce policy against the parsed query. Database permissions remain essential.

### 4.3 Example: controlled SQLite read-only execution

This teaching example uses SQLite and a tiny local database. It demonstrates opening the database in read-only mode and limiting returned rows. It is **not** a complete SQL security validator and must not be used as the sole defense for model-generated SQL.

```python
import sqlite3
from pathlib import Path

DB_PATH = Path("sales_demo.db")

def execute_prevalidated_select(sql: str, max_rows: int = 100):
    # This function assumes a separate, trusted SQL parser and policy
    # validator has already approved the query.
    if not DB_PATH.exists():
        raise FileNotFoundError(DB_PATH)

    uri = f"file:{DB_PATH.resolve().as_posix()}?mode=ro"
    conn = sqlite3.connect(uri, uri=True, timeout=3.0)

    try:
        conn.set_authorizer(
            lambda action, arg1, arg2, db_name, trigger_name:
                sqlite3.SQLITE_OK
                if action in {
                    sqlite3.SQLITE_SELECT,
                    sqlite3.SQLITE_READ,
                    sqlite3.SQLITE_FUNCTION,
                    sqlite3.SQLITE_RECURSIVE
                }
                else sqlite3.SQLITE_DENY
        )

        cursor = conn.execute(sql)
        columns = [item[0] for item in cursor.description or []]
        rows = cursor.fetchmany(max_rows + 1)

        if len(rows) > max_rows:
            rows = rows[:max_rows]

        return {
            "columns": columns,
            "rows": [tuple(row) for row in rows],
            "truncated": len(rows) == max_rows
        }
    finally:
        conn.close()
```

Important limitations:
- The query must be parsed and validated by a trusted, dialect-aware policy layer before calling this function.
- The SQLite authorizer is defense in depth, not a replacement for SQL parsing, database permissions, or query budgets.
- A row cap alone does not prevent an expensive query; add execution limits and resource controls appropriate to the database.
- In production, use a dedicated read-only principal and database-native policies.

### 4.4 Self-healing SQL

Self-healing means bounded correction of a query after a safe, classified error—not repeatedly trying arbitrary SQL until something works.

A safe loop:

1. Generate a candidate query.
2. Validate its syntax and policy.
3. Execute under read-only permissions and resource limits.
4. Classify the error.
5. If it is a correctable schema or syntax issue, provide sanitized error context and relevant authorized schema to the generator.
6. Revalidate the revised query from the beginning.
7. Stop after a small fixed number of attempts.
8. If the issue is authorization, policy, or ambiguity, do not retry around it; deny, clarify, or escalate.

Never let a model “fix” an authorization error by switching to a more privileged identity or a prohibited data source.

### Hands-on 4

Create a small SQLite sales database with sample tables. Implement a query pipeline that distinguishes syntax errors, missing columns, authorization failures, and timeouts. Permit at most two correction attempts for eligible syntax/schema errors. Verify that prohibited statements are rejected and that the database remains unchanged.

## 5. Data access controls

### 5.1 Allow-listed sources and query limits

Define allowed sources centrally. The model should not be able to supply an arbitrary database host, schema, file path, or connection string.

Controls to implement:

- Allow-listed database connections, schemas, tables, and views.
- Maximum rows, execution time, and result size.
- Maximum joins, query complexity, and concurrent requests where appropriate.
- Rate limits and cost controls.
- Deny-by-default behavior when a policy check cannot be completed.
- Cancellation of long-running queries.
- Safe error messages that do not expose database internals.

### 5.2 RBAC, row security, and column security

- **RBAC (role-based access control):** assigns permissions to roles such as analyst, support engineer, or manager.
- **Row-level security:** restricts which records an identity can access, for example to a permitted region or tenant.
- **Column-level security:** restricts sensitive fields such as salary, personal contact details, or payment identifiers.
- **Aggregation controls:** may be needed to reduce inference through repeated small queries or carefully chosen filters.

Apply controls in the database or a trusted data-access layer wherever possible. Do not depend on the model to hide restricted rows or columns after it has already retrieved them.

### 5.3 Prevent destructive queries and exfiltration

Potentially unsafe behaviors include:

- Attempting DDL/DML through a generated query.
- Reading tables outside the allowlist.
- Extracting excessive rows or sensitive columns.
- Using unauthorized joins or functions to reconstruct protected information.
- Asking the assistant to ignore policies embedded in tool results or user input.
- Repeatedly querying to infer restricted values.

Mitigations include least-privileged database identities, allowlists, parsed-query policies, database-native access controls, resource limits, result minimization, anomaly detection, and auditing.

### Hands-on 5

Define three roles—viewer, analyst, and administrator—for a demo sales dataset. Create a test matrix that checks permitted tables, restricted columns, row visibility, query limits, and prohibited operations. Verify access controls using the actual database identity or trusted enforcement layer, not only application-side filtering.

## 6. Platform portability: Azure, AWS, and Google Cloud

Enterprise services differ across cloud platforms, but the application architecture can remain portable if provider-specific capabilities are placed behind stable interfaces.

### 6.1 Capability mapping

| Capability | Azure examples | AWS examples | Google Cloud examples |
|---|---|---|---|
| Managed model access | Azure AI Foundry model services | Amazon Bedrock | Vertex AI |
| Identity and secrets | Microsoft Entra ID; Azure Key Vault | IAM; AWS Secrets Manager | Cloud IAM; Secret Manager |
| Search / retrieval | Azure AI Search | Amazon OpenSearch Service or an appropriate AWS search service | Vertex AI Search or an appropriate managed search service |
| Data access | Azure SQL / supported data services | Amazon RDS / supported data services | Cloud SQL / BigQuery and supported data services |
| Logging and monitoring | Azure Monitor / Application Insights | Amazon CloudWatch | Cloud Logging / Cloud Monitoring |

These are examples, not one-to-one equivalents. Service availability, features, model catalogs, and regional constraints change. Verify current service capabilities and organizational approvals before selecting a deployment.

### 6.2 Keep orchestration and evaluation portable

Separate provider-specific code from the core workflow:

```text
Application and policies
        |
        v
Portable orchestration + state machine
        |
        +---- Model adapter
        +---- Retrieval adapter
        +---- Tool/data adapter
        +---- Identity/secrets adapter
        +---- Evaluation interface
```

Use stable internal contracts for model invocation, retrieval, tool results, errors, and evaluation datasets. Keep provider-specific authentication, deployment identifiers, and request formats inside adapters.

Portability does not mean every provider supports identical models, structured-output behavior, tool calling, or latency. Run the same evaluation suite after changing a provider, and document differences.

### Hands-on 6

Create an adapter map for one enterprise copilot. Identify which parts remain provider-neutral and which are provider-specific. Define a smoke-test and evaluation checklist for migrating the model or search service to another cloud.

## 7. Day 24 practical: Secure Enterprise Copilot

### Scenario

Build an assistant that answers business questions over an approved sales dataset. Users ask questions in natural language; the assistant retrieves authorized schema and business definitions, proposes SQL, validates it, executes a read-only query, and returns a concise answer with a traceable query summary.

An alternative path is an MCP-enabled support copilot that discovers and invokes approved read-only tools. Students may choose either path, but must demonstrate access controls and safe failure behavior.

### Minimum architecture

```text
Authenticated user
       |
       v
Identity / tenant context
       |
       v
Intent + authorization checks
       |
       v
Schema or MCP capability discovery
       |
       v
LLM proposes query/action
       |
       v
Schema and policy validation
       |
       v
Read-only execution / approved tool
       |
       v
Result filtering + audit event
       |
       v
Answer or safe failure
```

### Required controls

- Authentication and explicit authorization.
- Tenant isolation and user-scoped context.
- Secrets held outside model prompts and source code.
- Allow-listed tools, data sources, tables, and columns.
- SQL parser/policy validation and read-only database identity.
- Row/result limits, timeout, and bounded self-healing.
- Database-enforced RBAC and row/column restrictions where applicable.
- Structured audit events with sensitive data minimized.
- Approval for high-impact actions.
- Clear safe failure behavior for ambiguity, denied access, timeouts, and missing evidence.

### Safe failure behavior

| Condition | Expected behavior |
|---|---|
| User request is ambiguous | Ask a clarifying question before querying |
| Table or column is not permitted | Deny the query without revealing protected schema details |
| SQL is invalid | Allow a bounded correction only for eligible errors |
| SQL violates policy | Reject it; do not retry with a bypass |
| Query exceeds resource limits | Cancel/stop and return a safe explanation |
| Tenant context is missing or invalid | Fail closed |
| MCP server or tool is unavailable | Return a controlled error or use an approved fallback |
| Human approval is pending | Pause; do not execute the action |
| Results may expose sensitive data | Apply policy-based filtering or refuse the result |

### Capstone deliverables

1. Architecture diagram and threat model.
2. Role/permission matrix and tenant-isolation design.
3. Runnable source code and setup instructions.
4. SQL validation and tool-security tests.
5. Audit-event examples with sensitive fields redacted.
6. Safe-failure test report.
7. Short portability note identifying provider-specific adapters and migration tests.

## 8. Evaluation and acceptance criteria

Measure behavior instead of judging the system only by whether it returns an answer.

| Metric | What to measure |
|---|---|
| Task completion | Questions answered correctly and within policy |
| SQL validity | Queries passing syntax and policy validation |
| Result correctness | Answers match trusted expected results |
| Access-control violations | Unauthorized data access attempts that were blocked; successful violations must be zero |
| Safe rejection | Prohibited requests denied without bypass |
| Query resource use | Runtime, rows scanned where available, rows returned, timeout rate |
| Self-healing | Eligible failures corrected within the retry budget |
| Audit completeness | Required security and operation fields present |
| Tenant isolation | Cross-tenant access attempts consistently denied |
| Latency and cost | End-to-end duration and model/service cost where available |

Use a fixed test dataset with both allowed and prohibited questions. Retain trace/request IDs so failures can be investigated without storing unnecessary sensitive content.

### Suggested test set

- Allowed aggregate question: “What was total sales by region last month?”
- Ambiguous metric: “What was revenue last quarter?”
- Restricted column request: “Show each customer's personal contact details.”
- Unauthorized table request.
- Injection-style user prompt asking to ignore access controls.
- Malformed or nonexistent column.
- Query that would exceed the row or time limit.
- Missing tenant identity.
- MCP server unavailable.
- Read/write action requiring approval.

## 9. Suggested implementation sequence

1. **Stage A — Data model:** create a small sample database and document allowed schema.
2. **Stage B — Identity and policy:** define roles, tenant boundaries, and source allowlists.
3. **Stage C — Schema and semantics:** add schema retrieval and a business glossary.
4. **Stage D — Query pipeline:** generate, parse, validate, and execute read-only SQL.
5. **Stage E — Reliability:** add query limits, classified errors, and bounded self-healing.
6. **Stage F — MCP option:** expose one safe capability through an MCP server or document a direct API alternative.
7. **Stage G — Audit:** record safe operational evidence and test sensitive-data redaction.
8. **Stage H — Portability:** map provider-specific adapters and run the same evaluation suite.
9. **Stage I — Security evaluation:** execute allowed, denied, ambiguous, timeout, and tenant-isolation tests.

## 10. Assessment rubric

| Area | Weight |
|---|---:|
| MCP architecture and integration choice | 10% |
| Authentication, authorization, and tenant isolation | 20% |
| NL-to-SQL schema retrieval and semantic disambiguation | 15% |
| SQL validation and read-only execution | 20% |
| Query controls and data security | 15% |
| Audit evidence and safe failure behavior | 10% |
| Portability and reproducible evaluation | 10% |

## 11. Final checklist

- [ ] MCP capability discovery is not confused with authorization.
- [ ] Direct API versus MCP choice has a documented rationale.
- [ ] Every request is associated with a trusted identity and tenant context.
- [ ] Secrets are outside prompts, source control, and ordinary traces.
- [ ] Tool, source, schema, table, and column access is allow-listed.
- [ ] SQL is parsed and policy-checked before execution.
- [ ] The database principal is read-only and least-privileged.
- [ ] Database-side row/column controls are used where supported.
- [ ] Query time, rows, result size, and correction attempts are bounded.
- [ ] Authorization and policy failures are not treated as repairable syntax errors.
- [ ] Audit events contain required operational evidence without unnecessary sensitive data.
- [ ] Tenant isolation is tested with adversarial cases.
- [ ] Ambiguous requests trigger clarification.
- [ ] Portability is tested through shared interfaces and the same evaluation suite.
- [ ] The assistant fails closed when identity, policy, or required controls are unavailable.

## References

- Model Context Protocol documentation: https://modelcontextprotocol.io/
- MCP specification: https://spec.modelcontextprotocol.io/
- LangChain MCP integrations: https://docs.langchain.com/oss/python/langchain/mcp
- LangGraph documentation: https://docs.langchain.com/oss/python/langgraph/overview
- OWASP Top 10 for LLM Applications: https://owasp.org/www-project-top-10-for-large-language-model-applications/
- Azure AI Foundry documentation: https://learn.microsoft.com/azure/ai-foundry/
- Amazon Bedrock documentation: https://docs.aws.amazon.com/bedrock/
- Vertex AI documentation: https://cloud.google.com/vertex-ai/docs
- Pydantic documentation: https://docs.pydantic.dev/

Check current official documentation for protocol versions, framework APIs, provider features, and security requirements before implementation. The examples are educational starter patterns; production deployment requires threat modeling, database-native permissions, security review, and environment-specific testing.
