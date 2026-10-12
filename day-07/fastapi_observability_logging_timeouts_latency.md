# FastAPI Observability: Structured Logging, Timeouts, and Latency Metrics

This note introduces three practical techniques for making a FastAPI service easier to debug, operate, and monitor.

## 1. Structured Logging

### What is structured logging?

Structured logging records log entries as fields—often JSON—instead of relying only on free-form text.

A plain-text log might look like this:

```text
2026-10-12 09:00:00 INFO GET /books completed in 42 ms
```

A structured JSON log might look like this:

```json
{
  "timestamp": "2026-10-12T09:00:00Z",
  "level": "INFO",
  "method": "GET",
  "path": "/books",
  "status_code": 200,
  "duration_ms": 42.0
}
```

Structured fields make logs easier to search, filter, aggregate, and analyze in tools such as OpenSearch, Elasticsearch, Loki, or a cloud logging platform.

### Why it is useful

- **Debugging:** Identify which endpoint failed and when.
- **Correlation:** Use a request ID to connect logs belonging to one request.
- **Monitoring:** Count errors and inspect slow requests.
- **Analysis:** Filter logs by endpoint, status code, duration, or environment.

### Example: Basic request logging middleware

```python
import logging
import time
from fastapi import FastAPI, Request

app = FastAPI()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("api")


@app.middleware("http")
async def log_requests(request: Request, call_next):
    start = time.perf_counter()

    try:
        response = await call_next(request)
    except Exception:
        duration_ms = (time.perf_counter() - start) * 1000
        logger.exception(
            "request_failed",
            extra={
                "method": request.method,
                "path": request.url.path,
                "duration_ms": round(duration_ms, 2),
            },
        )
        raise

    duration_ms = (time.perf_counter() - start) * 1000
    logger.info(
        "request_completed",
        extra={
            "method": request.method,
            "path": request.url.path,
            "status_code": response.status_code,
            "duration_ms": round(duration_ms, 2),
        },
    )
    return response


@app.get("/health")
async def health():
    return {"status": "ok"}
```

**Important:** Python's standard `logging` module does not automatically serialize `extra` fields as JSON. Configure a JSON formatter or use a structured-logging library such as `structlog` if machine-readable JSON output is required.

### Logging best practices

- Include timestamp, severity, request ID, HTTP method, route, status code, and duration where appropriate.
- Prefer `time.perf_counter()` for measuring elapsed time.
- Avoid logging passwords, access tokens, API keys, personal data, or request bodies containing sensitive information.
- Use `logger.exception()` inside an exception handler when a traceback is useful.
- Avoid logging the same exception at every layer.
- Use consistent field names and suitable log levels (`DEBUG`, `INFO`, `WARNING`, `ERROR`).

---

## 2. Timeouts

### What is a timeout?

A timeout limits how long an operation is allowed to wait. It helps prevent requests from waiting indefinitely for a slow dependency.

Common timeout types include:

- **Client timeout:** How long a client waits for the API response.
- **Outbound HTTP timeout:** How long the FastAPI service waits for another HTTP service.
- **Database timeout:** How long a database operation may run or wait.
- **Application/server timeout:** A limit enforced by the server or deployment platform.

These are different controls and should be configured at the appropriate layer.

### Example: Timeout for an outbound HTTP request

Install the HTTP client:

```bash
pip install httpx
```

Example FastAPI endpoint:

```python
import httpx
from fastapi import FastAPI, HTTPException

app = FastAPI()


@app.get("/external-data")
async def external_data():
    timeout = httpx.Timeout(5.0)

    try:
        async with httpx.AsyncClient(timeout=timeout) as client:
            response = await client.get(
                "https://httpbin.org/delay/2"
            )
            response.raise_for_status()
            return response.json()

    except httpx.TimeoutException:
        raise HTTPException(
            status_code=504,
            detail="The upstream service timed out",
        )

    except httpx.HTTPError:
        raise HTTPException(
            status_code=502,
            detail="The upstream service request failed",
        )
```

Here, the HTTP client is configured with a five-second timeout. HTTPX supports more detailed timeout configuration for connection, read, write, and connection-pool operations.

### Timeout considerations

- Choose timeout values based on the endpoint's purpose and the dependency's expected response time.
- Set explicit timeouts for outbound HTTP calls and database operations.
- Return an appropriate error response when a dependency times out; `504 Gateway Timeout` is often suitable when acting as a gateway to an upstream service.
- A client disconnect or timeout does **not** guarantee that all server-side work has stopped.
- Configure server and proxy timeouts separately. A reverse proxy or load balancer may time out before the application does.
- Do not retry indefinitely. If retries are appropriate, use a retry limit, backoff, and an overall deadline.

---

## 3. Latency Metrics

### What is latency?

Latency is the elapsed time between a request starting and a response being produced. In a web service, it is commonly measured in milliseconds.

Latency metrics help answer questions such as:

- Which endpoints are slow?
- Are response times getting worse after a deployment?
- Are a small number of requests much slower than the rest?
- Does the service meet its performance target?

### Percentiles: p50, p95, and p99

Percentiles describe the distribution of request durations.

| Metric | Meaning | Example |
|---|---|---:|
| **p50** | Median latency; about 50% of requests complete at or below this value | 100 ms |
| **p95** | About 95% of requests complete at or below this value | 300 ms |
| **p99** | About 99% of requests complete at or below this value | 800 ms |

Interpretation of these example values:

- **p50 = 100 ms:** A typical request completes within roughly 100 ms.
- **p95 = 300 ms:** Around 5% of requests take longer than 300 ms.
- **p99 = 800 ms:** Around 1% of requests take longer than 800 ms.

Percentiles reveal slow outliers that an average can hide. For example, most requests may take 100 ms while a small number take several seconds.

### Example: Measure request duration in middleware

```python
import time
from fastapi import FastAPI, Request

app = FastAPI()


@app.middleware("http")
async def measure_latency(request: Request, call_next):
    start = time.perf_counter()

    response = await call_next(request)

    duration_seconds = time.perf_counter() - start
    response.headers["X-Process-Time"] = f"{duration_seconds:.4f}"

    return response


@app.get("/items")
async def list_items():
    return {"items": ["pen", "book", "notebook"]}
```

This example adds an `X-Process-Time` response header containing the measured duration in seconds. It is a simple demonstration, not a substitute for production metrics. If an exception is raised, this minimal middleware does not add the header.

### Metrics to monitor

| Metric | What it tells you |
|---|---|
| Request count / throughput | How many requests the service handles |
| Latency p50 | Typical response time |
| Latency p95 | Response time for most requests |
| Latency p99 | Tail latency and slow outliers |
| HTTP 4xx rate | Frequency of client-side errors |
| HTTP 5xx rate | Frequency of server-side errors |
| Timeout count | How often operations exceed their time limits |
| In-flight requests | Number of requests currently being processed |

### Prometheus and Grafana

For production monitoring, expose metrics in a format Prometheus can scrape and use Grafana to build dashboards and alerts.

Install the instrumentation package:

```bash
pip install prometheus-fastapi-instrumentator
```

Example:

```python
from fastapi import FastAPI
from prometheus_fastapi_instrumentator import Instrumentator

app = FastAPI()

Instrumentator().instrument(app).expose(app)


@app.get("/health")
async def health():
    return {"status": "ok"}
```

Run the service with Uvicorn:

```bash
uvicorn main:app --reload
```

The instrumentator exposes a Prometheus metrics endpoint (commonly `/metrics`). Verify the configured endpoint and metrics in your installed package version. Prometheus must be configured to scrape it, and Grafana must be connected to the relevant data source to display dashboards.

### Service-level objectives (SLOs)

An SLO is a measurable target for service performance. For example:

> 95% of successful requests should complete within 300 ms over a rolling 30-day window.

The exact target should be based on user needs and measured baseline performance. Define whether the SLO includes errors, which endpoints it covers, and how the measurement window is calculated.

---

## 4. How the Three Practices Work Together

| Practice | Main question answered | Example |
|---|---|---|
| Structured logging | What happened on a particular request? | Request ID, endpoint, status, exception |
| Timeouts | How long should an operation wait? | Stop waiting for an upstream HTTP response after the configured limit |
| Latency metrics | How fast is the service over time? | p50, p95, p99 latency dashboards |

A practical production setup combines all three:

1. **Log** each request with consistent fields and a request ID.
2. **Set timeouts** for external dependencies and coordinate them with server and proxy limits.
3. **Measure latency** using histograms or equivalent distribution metrics.
4. **Monitor errors and timeouts** alongside request volume and latency.
5. **Alert on SLO violations** rather than relying only on averages.
6. **Protect sensitive data** in both logs and metrics.

## 5. Quick Checklist

- [ ] Structured logs include request context and duration.
- [ ] Sensitive values are excluded from logs.
- [ ] Outbound HTTP and database operations have explicit timeouts.
- [ ] Retries are bounded and safe for the operation.
- [ ] Latency is measured with a monotonic timer such as `time.perf_counter()`.
- [ ] p50, p95, and p99 latency are tracked.
- [ ] 4xx, 5xx, and timeout rates are monitored.
- [ ] Prometheus/Grafana or an equivalent observability platform is configured.
- [ ] Performance targets and alert thresholds are documented.
