# Production MLOps: Concepts, Definitions, Explanations, and AWS Examples

This reference guide extracts the key concepts from the Day 12–15 curriculum and the Production Readiness Project. Each concept includes a clear definition, explanation, and practical example using AWS services where relevant.

## Running Example

Use an **Iris Classification API** throughout the workshop. It loads a registered ML model, accepts prediction requests through FastAPI, and runs on Amazon ECS with AWS monitoring and security controls.

---

# 1. Cloud-Neutral AI Architecture

## 1.1 Cloud-Neutral Architecture

**Definition:** An architecture designed so that an application's core functionality can run on different cloud platforms with minimal or no changes to its business logic.

**Explanation:** Cloud neutrality separates the model, inference code, data contracts, and application configuration from cloud-specific infrastructure such as storage, identity, networking, and deployment services.

**Example:** A FastAPI service exposes `/predict`. It can run on AWS ECS, Azure Container Apps, or Google Cloud Run if each platform supplies the required configuration, identity, storage access, and networking.

Cloud-neutral does not mean every infrastructure resource is identical across clouds. It means cloud-specific differences are isolated behind clear interfaces.

## 1.2 Portable Service Mapping

**Definition:** Mapping a logical capability required by an application to the corresponding service on each cloud provider.

| Logical capability | AWS | Azure | Google Cloud |
|---|---|---|---|
| Object storage | Amazon S3 | Azure Blob Storage | Cloud Storage |
| Container compute | Amazon ECS/Fargate | Azure Container Apps | Cloud Run |
| Container registry | Amazon ECR | Azure Container Registry | Artifact Registry |
| Secret management | AWS Secrets Manager | Azure Key Vault | Secret Manager |
| Workload identity | IAM roles | Managed identities | Service accounts |
| Monitoring | Amazon CloudWatch | Azure Monitor | Cloud Monitoring |
| Virtual networking | Amazon VPC | Azure Virtual Network | VPC |

**Example:** The application needs a model artifact. On AWS, it reads from S3; on Azure, it reads from Blob Storage. The storage adapter and deployment configuration may change, while the prediction interface remains the same.

## 1.3 Managed ML Capabilities

**Definition:** Cloud-provider services that manage parts of the machine-learning lifecycle, including training, model registration, deployment, and monitoring.

| ML lifecycle stage | AWS | Azure | Google Cloud |
|---|---|---|---|
| Managed training | Amazon SageMaker Training | Azure Machine Learning | Vertex AI Training |
| Model registry | SageMaker Model Registry | Azure ML registry | Vertex AI Model Registry |
| Managed inference | SageMaker endpoints | Azure ML online endpoints | Vertex AI endpoints |
| Pipeline orchestration | SageMaker Pipelines | Azure ML pipelines | Vertex AI Pipelines |
| ML monitoring | SageMaker monitoring capabilities and CloudWatch | Azure ML monitoring capabilities | Vertex AI model monitoring capabilities |

**Example:** Train an Iris classifier using SageMaker, register version 3, evaluate it against version 2, and deploy the approved version to a SageMaker endpoint.

**Key distinction:** ECS/Fargate is a general-purpose container platform. SageMaker provides ML-oriented managed capabilities. They solve related but different operational problems.

## 1.4 Application–Infrastructure Separation

**Definition:** Keeping application code independent from the code that creates and configures the infrastructure on which it runs.

- **Application:** FastAPI routes and model prediction logic.
- **Infrastructure:** ECS service, load balancer, IAM roles, VPC, and CloudWatch log group.
- **Configuration:** Model version, environment, port, and resource settings.

**Example:** Deploy the same application image to development, staging, and production using different infrastructure and configuration.

---

# 2. Identity and Security

## 2.1 Workload Identity

**Definition:** An identity assigned to an application, service, or workload so it can authenticate to other resources without embedded credentials.

**Example:** An ECS task receives an IAM task role that permits access to a specific S3 model-artifact prefix.

```text
FastAPI container
       |
       | Uses task role
       v
AWS IAM authorization
       |
       v
Approved S3 model artifacts
```

The application does not need an AWS access key and secret key inside its source code.

## 2.2 IAM Roles, Service Accounts, and Managed Identities

**Definition:** Platform-specific mechanisms for assigning permissions to workloads.

- **AWS IAM role:** An identity with permissions that an authorized workload can assume.
- **Azure managed identity:** An identity managed by Azure and assigned to a supported resource or workload.
- **Google Cloud service account:** An identity used by an application or workload to access Google Cloud resources.

**Example:** The Iris API needs permission to read a model from object storage. Assign it an AWS task role, Azure managed identity, or Google Cloud service account.

The application-level requirement is the same, but identity setup and authorization policies differ by platform.

## 2.3 Least Privilege

**Definition:** Granting a user or workload only the permissions required to perform its assigned tasks.

**Example:** A prediction service that only reads model artifacts should not receive unrestricted access to every S3 bucket.

Example policy for a dedicated model-artifact prefix:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": ["s3:GetObject"],
      "Resource": "arn:aws:s3:::YOUR-MODEL-BUCKET/models/*"
    }
  ]
}
```

Replace the placeholder bucket name and prefix. Add `s3:ListBucket` only if listing is required, with a suitable bucket-level resource and restrictions.

## 2.4 Secret Management

**Definition:** Secure storage, access, rotation, and auditing of sensitive values such as API tokens, database passwords, and private keys.

**Example:** Store a database password in AWS Secrets Manager and authorize the workload to retrieve it when required.

| Configuration | Example | Recommended treatment |
|---|---|---|
| Ordinary configuration | API port `8000` | Environment configuration |
| Sensitive credential | Database password | Secrets Manager |
| AWS resource access | Read model from S3 | IAM task role |
| Model selection | `IrisClassifier` version `3` | Versioned deployment configuration |

Do not embed secrets in source code, container images, or committed configuration files.

## 2.5 Network and Data Protection

**Definition:** Controls that protect communications, infrastructure access, stored data, and sensitive information.

**AWS example:**
- Place ECS tasks in appropriately configured VPC subnets.
- Expose the API through an Application Load Balancer.
- Restrict security group rules to required traffic.
- Use HTTPS for client connections.
- Apply encryption and access controls to S3 and other data stores.
- Prevent secrets and sensitive prediction inputs from appearing in logs.

---

# 3. Infrastructure Delivery

## 3.1 Infrastructure as Code (IaC)

**Definition:** Managing infrastructure through version-controlled, machine-readable configuration rather than creating every resource manually.

**AWS example:** Use Terraform to define an ECS service, ECR repository, IAM roles, security groups, and CloudWatch log groups.

```bash
terraform init
terraform fmt -check
terraform validate
terraform plan
```

After reviewing the plan, apply it to the intended environment:

```bash
terraform apply
```

Terraform describes desired infrastructure state and calculates the required changes.

## 3.2 Reusable Infrastructure Modules

**Definition:** Self-contained infrastructure definitions that can be reused with different inputs.

**Example:**

| Parameter | Development | Production |
|---|---|---|
| Desired tasks | 1 | 2 or more, as required |
| CPU and memory | Small | Based on load testing |
| Logging retention | Shorter | According to retention policy |
| Traffic exposure | Restricted | Approved production ingress |
| Scaling | Minimal | Defined scaling policy |

Use the same module with different inputs. Choose production values based on availability and workload requirements.

## 3.3 Environment Configuration

**Definition:** Settings that control how an application behaves in a particular environment without changing its business logic.

```text
APP_ENV=staging
MODEL_NAME=IrisClassifier
MODEL_VERSION=3
LOG_LEVEL=INFO
```

Sensitive values should be supplied through an appropriate secret-management mechanism rather than ordinary environment files committed to source control.

## 3.4 Boto3

**Definition:** The AWS SDK for Python, used to interact with AWS services programmatically.

**Example: List objects in an S3 model-artifact bucket**

```python
import boto3

s3 = boto3.client("s3")

response = s3.list_objects_v2(
    Bucket="YOUR-MODEL-BUCKET",
    Prefix="models/",
)

for item in response.get("Contents", []):
    print(item["Key"])
```

The workload needs appropriate `s3:ListBucket` permission for the bucket and prefix. Use an IAM role or another approved credential provider rather than hardcoding access keys.

## 3.5 Architecture Translation Exercise

**Definition:** Re-expressing an application's infrastructure design on another cloud while preserving its functional requirements and application interfaces.

**Example:** Translate the Iris service from AWS to Google Cloud:

- S3 → Cloud Storage
- ECR → Artifact Registry
- ECS/Fargate → Cloud Run
- Secrets Manager → Secret Manager
- CloudWatch → Cloud Logging and Cloud Monitoring

**What remains unchanged:** Prediction schema, core model inference logic, API contract, and application-level tests.

**What may change:** Identity configuration, networking, resource definitions, deployment pipelines, telemetry integrations, and cloud-specific SDK code.

---

# 4. Production Model Serving

## 4.1 Model Serving

**Definition:** Making a trained model available to consumers so it can generate predictions on demand or in scheduled processing jobs.

**Example:** Deploy a FastAPI application to ECS/Fargate, load the approved Iris model, and expose `/predict` through an Application Load Balancer.

## 4.2 Batch Inference

**Definition:** Processing a collection of input records together, typically on a schedule or when a dataset becomes available.

**Example:** Every night, score 500,000 customer records stored in S3 and write the predictions back to S3.

**AWS services:** S3 with SageMaker Processing, AWS Batch, or an appropriately configured ECS task.

Batch inference is useful when immediate responses are unnecessary and processing efficiency matters more than per-request latency.

## 4.3 Asynchronous Inference

**Definition:** Accepting a prediction request for processing and returning a job identifier or acknowledgement before the final result is ready.

**Example:** A document classification application accepts a PDF, adds a job to Amazon SQS, and processes it using ECS workers. The user retrieves the result later.

This pattern is appropriate for long-running tasks, buffering, retries, and independent workers.

## 4.4 Real-Time Inference

**Definition:** Returning a prediction within the same request-response interaction.

**Example:** A checkout service sends transaction features to an inference API and receives a risk score before completing the transaction.

**AWS services:** ECS/Fargate behind an Application Load Balancer or a SageMaker real-time endpoint.

## 4.5 Latency, Throughput, Freshness, and Cost

| Concept | Definition | Example measurement |
|---|---|---|
| Latency | Time taken to complete one request | p95 latency = 180 ms |
| Throughput | Work completed per unit of time | 250 requests/second |
| Freshness | How current input data or a prediction is | Data updated every 5 minutes |
| Cost | Resources and services consumed to produce predictions | Cost per 1,000 predictions |

**Example:** A fraud API may need a response within 200 ms, whereas a nightly customer segmentation job can take hours.

Optimizing only latency can increase cost. Optimizing only cost can cause unacceptable delays.

## 4.6 Scalability

**Definition:** The ability of a system to handle changing workloads by adjusting resources or distributing work.

- **Vertical scaling:** Increase CPU or memory for an instance or task.
- **Horizontal scaling:** Add more instances or tasks.

**AWS example:** Configure ECS Service Auto Scaling to increase inference tasks when demand rises and reduce capacity when demand falls, subject to minimum and maximum limits.

## 4.7 Reliability

**Definition:** The ability of a service to continue providing required functionality despite expected failures.

**AWS example:** Run multiple ECS tasks, configure health checks, use an appropriate load-balancer target group, and configure deployment rollback behavior.

A health check should distinguish process health from readiness to serve predictions when those conditions differ.

## 4.8 Model Registry

**Definition:** A controlled repository of model versions and associated metadata, artifacts, and lifecycle information.

**Example:** An MLflow registry contains `IrisClassifier` versions 2 and 3. Version 3 becomes the approved candidate only after passing evaluation.

The registry is not necessarily the runtime model server. The serving application must retrieve or receive the approved artifact and load it.

---

# 5. Release Strategies

## 5.1 Shadow Deployment

**Definition:** Sending copies of eligible production requests to a candidate model while continuing to use the existing model's predictions for actual decisions.

**Example:** Iris v1 generates the response returned to the client, while Iris v2 receives the same inputs and its output is recorded for comparison.

Shadowing helps evaluate latency, errors, and prediction differences without exposing users to candidate decisions. Prevent duplicate business actions and protect sensitive data copied to the candidate service.

## 5.2 Canary Deployment

**Definition:** Releasing a new version to a small portion of traffic before gradually increasing its exposure.

**Example:** Route 10% of eligible requests to v2 and 90% to v1. Expand only if latency, errors, and quality checks meet their thresholds.

## 5.3 Blue-Green Deployment

**Definition:** Maintaining two separate deployment environments and switching traffic from the current environment to the replacement after validation.

**Example:** Blue runs Iris v1; green runs Iris v2. After successful testing, traffic moves to green. If the new version fails, traffic can return to blue, provided the previous environment remains available and compatible.

## 5.4 Model-Version Comparison

**Definition:** Evaluating two or more model versions against consistent data and predefined evaluation criteria.

**Example:** Compare Iris v2 and v3 using the same held-out dataset, measuring accuracy, per-class performance, inference latency, and prediction differences.

For business-critical models, consider precision, recall, false-positive rate, and the cost of incorrect decisions.

## 5.5 Rollback Triggers

**Definition:** Predefined conditions that require stopping a rollout or restoring a previous known-good release.

**Examples:**
- Error rate exceeds the agreed limit.
- p95 latency exceeds the service-level objective.
- The model produces invalid outputs.
- Quality checks fail.
- A security issue is detected.

**AWS example:** Configure deployment alarms and supported rollback behavior for the chosen ECS deployment strategy, or use SageMaker endpoint deployment controls where applicable.

A rollback should restore a known-good combination of application image, model version, and configuration.

---

# 6. Performance Engineering

## 6.1 Load Testing

**Definition:** Measuring system behavior while subjecting it to a specified workload.

**Example:** Generate 100 concurrent users against the Iris API and measure latency percentiles, requests per second, and failed requests.

Tools include Locust, k6, and JMeter.

## 6.2 Latency Percentiles

**Definition:** Statistical measures describing how long requests take for a given proportion of requests.

- **p50:** Half of requests complete at or below this latency.
- **p95:** 95% of requests complete at or below this latency.
- **p99:** 99% of requests complete at or below this latency.

**Example:** If p50 is 40 ms but p99 is 900 ms, most requests are fast, but a small proportion experience significant delays.

Percentiles reveal tail latency that averages can conceal.

## 6.3 Throughput

**Definition:** The rate at which a system processes work successfully.

**Example:** An API processes 800 successful requests per second under a defined workload.

Report throughput alongside workload, latency, error rate, and resource configuration. A high request rate accompanied by a high failure rate is not successful capacity.

## 6.4 Saturation

**Definition:** The degree to which a system's available resources are being consumed.

**Examples:**
- CPU utilization remains near its limit.
- Memory pressure causes task failures.
- A worker queue grows continuously.
- Database connection pools are exhausted.

**AWS example:** Monitor ECS CPU and memory, load-balancer metrics, and application-specific queue depth. Scale or optimize based on the actual bottleneck.

## 6.5 Resilience Testing

**Definition:** Testing how a service responds to failures and degraded dependencies.

**Example:** Make model-artifact storage temporarily unavailable in a test environment and verify that the service reports an error safely rather than returning an incorrect prediction.

Other tests include container restarts, dependency timeouts, invalid inputs, and insufficient worker capacity. Define expected behavior and success criteria before injecting a fault.

---

# 7. Observability

## 7.1 Observability

**Definition:** The ability to understand a system's internal state from the telemetry it emits.

The three commonly discussed signals are logs, metrics, and traces.

## 7.2 Logs

**Definition:** Timestamped records of events that occurred in an application or system.

**Example:** The Iris API logs a model-loading failure, including a request or deployment correlation identifier where appropriate.

**AWS service:** CloudWatch Logs.

Use structured logs with consistent fields. Avoid recording credentials, sensitive inputs, or unnecessary personal data.

## 7.3 Metrics

**Definition:** Numerical measurements collected over time to describe system behavior.

**Examples:**
- Requests per minute.
- Error rate.
- p95 latency.
- CPU utilization.
- Prediction counts by class.

**AWS service:** CloudWatch Metrics, including custom application metrics published through an appropriate mechanism.

Metrics support dashboards, alert thresholds, and trend analysis.

## 7.4 Distributed Traces

**Definition:** Records showing the sequence and duration of operations involved in processing a request across components.

**Example:** A request enters the load balancer, reaches FastAPI, calls a model registry or feature service, and returns a response. A trace helps identify which operation caused delay.

**AWS tooling:** AWS X-Ray and compatible OpenTelemetry instrumentation.

## 7.5 Correlation Identifiers

**Definition:** Identifiers used to connect related events across logs, traces, and services.

**Example:** A prediction request has ID `req-001`. The API log and associated trace use the same identifier so an engineer can investigate the request across components.

Correlation identifiers should not contain secrets or sensitive personal information.

## 7.6 Prediction-Distribution Monitoring

**Definition:** Monitoring how frequently a model produces different predictions or scores over time.

**Example:** Suddenly, 99% of Iris predictions belong to one class. This may indicate a change in incoming data, a preprocessing defect, or a model issue.

Prediction drift should trigger investigation, not an automatic conclusion that accuracy has deteriorated.

---

# 8. Monitoring and Response

## 8.1 Data Quality

**Definition:** The degree to which data is valid, complete, consistent, and suitable for its intended use.

**Example:** An Iris API receives a negative sepal length or a missing feature. The service rejects the request instead of silently generating a prediction.

Checks include missing values, unexpected types, invalid ranges, duplicates where uniqueness is required, unexpected categories, and schema changes.

## 8.2 Data Drift

**Definition:** A change in the distribution or characteristics of input data compared with a reference dataset.

**Example:** A production service starts receiving much larger petal measurements than those found in its training dataset.

Data drift is an early-warning signal. It does not necessarily mean model performance has declined.

## 8.3 Concept Drift

**Definition:** A change in the relationship between model inputs and the outcomes the model is expected to predict.

**Example:** A fraud model becomes less effective because fraudulent behavior changes, even though input feature distributions appear similar to those seen during training.

Concept drift often requires labeled outcomes to confirm.

## 8.4 Model-Performance Decay

**Definition:** A deterioration in predictive performance relative to an agreed baseline or acceptance threshold.

**Example:** A classification model's measured accuracy falls from 95% to 82% on a sufficiently representative labeled evaluation set.

Check label quality, sampling bias, feature changes, and model behavior before deciding whether retraining is necessary.

## 8.5 Alerting

**Definition:** Generating a notification when a monitored metric or condition meets a defined rule.

**AWS example:** A CloudWatch alarm detects sustained elevated target response time and sends a notification through Amazon SNS.

A useful alert specifies the condition, evaluation window, severity, affected service, responsible team, initial investigation steps, and escalation path.

## 8.6 Retraining Triggers

**Definition:** Explicit conditions that initiate model retraining or a model-review workflow.

**Examples:**
- Model quality falls below an agreed threshold.
- A material change in the input population is confirmed.
- Sufficient new labeled data becomes available.
- A scheduled retraining date is reached.

**AWS example:** CloudWatch or a scheduled workflow triggers a pipeline implemented with SageMaker Pipelines or AWS Step Functions.

Retraining should not automatically imply production promotion. The new candidate must pass validation, evaluation, and any required approval gate.

---

# 9. Governance and Risk

## 9.1 Operational Controls

**Definition:** Policies, permissions, procedures, and technical safeguards that govern how a model is developed, released, and operated.

**Example:** Only authorized users can approve production model releases, while the inference task role has read-only access to the model artifacts it needs.

## 9.2 Approvals

**Definition:** Explicit authorization required before a defined operation or release can proceed.

**Example:** A candidate model passes automated tests but cannot be promoted to production until the designated approver authorizes the release.

Human approval does not replace required technical quality checks.

## 9.3 Audit Trails

**Definition:** Records of actions and events that allow an organization to reconstruct what happened, when it happened, and who or what initiated it.

**AWS example:** CloudTrail records supported AWS API activity, while the deployment pipeline records the model version, release manifest, test results, and approval information.

CloudTrail is not a complete record of every inference request or application event. Application logs and registry metadata provide complementary evidence.

## 9.4 Model Lineage

**Definition:** The traceable relationship between data, code, configuration, training run, model artifact, and deployed release.

```text
Dataset version
      ↓
Training code commit
      ↓
MLflow run ID
      ↓
IrisClassifier v3
      ↓
Container image digest
      ↓
ECS deployment revision
```

Lineage helps identify exactly which model and software version generated a prediction.

## 9.5 Retention

**Definition:** The period for which logs, datasets, artifacts, and audit records are preserved.

**Example:** Keep operational logs for a defined period, preserve approved model artifacts according to the model-retention policy, and apply lifecycle rules to old S3 objects.

Retention must balance investigation needs, legal obligations, privacy requirements, and storage cost.

## 9.6 Human Escalation

**Definition:** A defined process for referring decisions or incidents to a qualified person when automated systems cannot safely resolve them.

**Example:** If a high-impact prediction has low confidence or the model detects an unfamiliar input, the application routes the case for human review rather than making an irreversible decision automatically.

Specify who reviews the case, how quickly it must be handled, and what happens while a decision is pending.

---

# 10. Cost and Sustainability

## 10.1 Cost Estimation

**Definition:** Estimating the financial cost of the infrastructure and services required to operate a workload.

**AWS example:** Estimate ECS/Fargate compute, Application Load Balancer, ECR storage, S3 storage, CloudWatch ingestion and retention, and data transfer.

Use the AWS Pricing Calculator before deployment and Cost Explorer or billing data to compare estimates with actual usage.

## 10.2 Right-Sizing

**Definition:** Selecting resource allocations that satisfy workload requirements without paying for excessive unused capacity.

**Example:** Load testing reveals that a small ECS task handles the target request rate with adequate latency and memory headroom. The team avoids deploying a much larger task without evidence that it is needed.

Consider peak traffic, model loading, concurrency, memory usage, and safety margins—not just average CPU utilization.

## 10.3 Autoscaling

**Definition:** Automatically increasing or decreasing service capacity in response to demand or resource signals.

**AWS example:** ECS Service Auto Scaling adjusts the desired task count based on CPU utilization, request load, or a suitable custom metric.

Autoscaling needs minimum and maximum limits, suitable evaluation windows, and enough capacity to absorb traffic while new tasks start.

## 10.4 Cost–Accuracy–Latency Trade-Offs

**Definition:** Choosing a configuration that balances predictive quality, response time, reliability, and operational expense.

**Example:** A larger model might improve accuracy but require more memory and CPU, increasing cost and potentially reducing throughput. A smaller model might be cheaper and faster but miss important cases.

Compare candidate models under equivalent evaluation data and serving workloads before choosing.

---

# 11. Production Readiness Project

## 11.1 Data Pipeline

**Definition:** An automated sequence of steps that prepares data for training or inference.

**Example:** S3 stores training data, a validation step checks schema and data quality, and a training job consumes the validated dataset.

A robust pipeline makes its inputs, outputs, dependencies, and failure conditions explicit.

## 11.2 Automated Training Workflow

**Definition:** A repeatable workflow that executes training, evaluation, and model-registration steps with minimal manual intervention.

**AWS example:** SageMaker Pipelines orchestrates preprocessing, training, evaluation, and conditional registration of the candidate model.

Record the dataset reference, code version, parameters, metrics, and artifacts to support investigation and reproducibility.

## 11.3 Quality Gates

**Definition:** Conditions that must be satisfied before a pipeline or release can progress to the next stage.

**Example:** Reject a model candidate if its recall falls below the required threshold or if its API integration tests fail.

Quality gates can include data validation, predictive performance, fairness checks where relevant, security scans, latency, and deployment health.

## 11.4 Automated Tests

**Definition:** Tests executed by software to verify expected behavior and detect regressions.

Types include:
- **Unit tests:** Validate individual functions and preprocessing logic.
- **API tests:** Check request validation and response structure.
- **Integration tests:** Verify interactions with the registry, storage, and serving environment.
- **Model tests:** Check evaluation metrics and expected prediction behavior.
- **Deployment tests:** Confirm health, readiness, and post-release behavior.

**Example:** A CI pipeline rejects a release if `/predict` returns an invalid response schema or the candidate model fails its minimum evaluation threshold.

## 11.5 Pipeline Failure Handling

**Definition:** Detecting, reporting, and recovering from failures in an automated workflow.

**Example:** A training job fails because the dataset has an unexpected schema. The pipeline stops before registering the candidate model, records the error, and alerts the responsible team.

Distinguish retryable failures, such as temporary network errors, from permanent failures, such as invalid input data.

## 11.6 Release Evidence

**Definition:** Recorded proof that a model release satisfied required technical and governance conditions.

**Example:** A release package contains:
- Automated test results.
- Model evaluation metrics.
- Registry version and run ID.
- Image digest.
- Security scan results.
- Approval record.
- Deployment revision.
- Post-deployment health metrics.
- Rollback target.

This evidence makes release decisions reviewable and auditable.

## 11.7 Reliability Scenarios

**Definition:** Deliberately testing realistic failure conditions to verify that the system behaves as expected.

**Examples:**
- Bad input data is rejected.
- A failed training job does not promote a candidate.
- A latency spike triggers investigation or scaling.
- A faulty model release is rolled back.
- A missing model artifact causes a clear failure rather than fabricated predictions.

The objective is to demonstrate that the system can fail safely and recover predictably.

## 11.8 Architecture Review

**Definition:** A structured assessment of whether the system meets its functional, security, operational, and business requirements.

The team should be able to explain:
1. Which components are portable and which are cloud-specific.
2. How workloads authenticate and obtain permissions.
3. How models are trained, registered, approved, and deployed.
4. How releases are evaluated and rolled back.
5. How failures and model drift are detected.
6. How cost is estimated and controlled.
7. Who owns operations and incident response.
8. Which limitations and risks remain unresolved.

---

# 12. Quick Concept Reference

| Concept | Remember it as |
|---|---|
| Cloud-neutral architecture | Same application contract across clouds |
| Service mapping | Equivalent cloud capabilities |
| Workload identity | How an application proves who it is |
| Least privilege | Only the permissions required |
| Secrets management | Secure handling of credentials |
| Infrastructure as Code | Infrastructure defined and version-controlled as code |
| Boto3 | Python interface to AWS APIs |
| Batch inference | Many records processed together |
| Asynchronous inference | Submit now, retrieve results later |
| Real-time inference | Request and response in the same interaction |
| Scalability | Adapt capacity to workload |
| Reliability | Continue operating or recover safely |
| Shadow deployment | Compare a candidate without using its decisions |
| Canary deployment | Gradually expose traffic to a new release |
| Blue-green deployment | Switch between separate environments |
| Load testing | Measure behavior under a defined workload |
| Observability | Understand system behavior from telemetry |
| Data drift | Input data distribution changes |
| Concept drift | Input-to-outcome relationship changes |
| Model lineage | Trace data and code to the deployed model |
| Quality gate | Required condition before progression |
| Rollback | Restore a known-good release |
| Cost-aware operations | Meet requirements at a sustainable cost |
| Production readiness | Demonstrated ability to deploy, monitor, secure, and recover |

## Final Takeaway

**Production MLOps is not just model deployment.** It is the disciplined management of the complete lifecycle—from data and training through release, monitoring, governance, and recovery.
