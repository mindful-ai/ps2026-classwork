# Quality Gates and Release Testing

In software/ML, **quality gates** and **release testing** are controls used to make sure software is good enough before it moves to the next stage or reaches users.

## 1. Quality Gates

A **quality gate** is a **predefined pass/fail checkpoint**.

For example, before an ML model can be deployed:

| Quality Gate | Requirement | Result |
|---|---|---|
| Unit tests | 100% pass | ✅ |
| Model accuracy | ≥ 90% | ✅ |
| F1-score | ≥ 0.85 | ✅ |
| Data validation | No critical errors | ✅ |
| Security scan | No critical vulnerabilities | ❌ |
| Code coverage | ≥ 80% | ✅ |

If a critical gate fails:

```text
Code / Model
     ↓
Quality Gates
     ↓
   FAIL ❌
     ↓
Fix required
```

The release is **blocked**.

Think of a quality gate as:

> **"Are we good enough to proceed?"**

## 2. Release Testing

**Release testing** is the testing performed on a version that is intended to be released.

For example:

```text
Developer Code
      ↓
Unit Testing
      ↓
Integration Testing
      ↓
System Testing
      ↓
Release Testing
      ↓
Production
```

Release testing typically checks things such as:

- Does the complete application work?
- Do APIs work correctly?
- Does the UI work?
- Does the model produce acceptable predictions?
- Does the application work with real-like data?
- Are there performance problems?
- Are there security issues?
- Does deployment work correctly?

## Simple Distinction

### Quality Gate = Decision Point

> "Does this version meet our predefined criteria?"

### Release Testing = Testing Activity

> "Let's test the release candidate to determine whether it is ready."

## In an ML/MLOps Project

For example, your **customer churn model** might have:

```text
New Model
   ↓
Unit Tests
   ↓
Data Validation
   ↓
Model Evaluation
   ↓
Quality Gates
   ├── Accuracy ≥ 85%       ✅
   ├── F1 ≥ 80%             ✅
   ├── ROC-AUC ≥ 85%        ✅
   ├── No data leakage      ✅
   └── Inference < 100 ms   ❌
              ↓
           BLOCK ❌
```

Even though the model has good accuracy, the **release is blocked** because inference performance failed the quality gate.

## In Short

> **Release testing produces evidence; quality gates use that evidence to decide whether the release can proceed.**
