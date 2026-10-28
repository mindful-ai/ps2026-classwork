# Types of Testing in the Software Development Life Cycle (SDLC)

Software testing is performed throughout the Software Development Life Cycle (SDLC) to verify that software meets requirements, works correctly, performs efficiently, remains secure, and provides a good user experience.

Testing types can be classified by **testing level, purpose, execution method, and stage of development**.

## 1. Testing by Level

These are the fundamental testing levels used in most software projects.

| Type | What it tests | Example |
|---|---|---|
| Unit Testing | Individual functions, methods, or components | Test a Python function that calculates tax |
| Integration Testing | Interaction between modules or services | Verify that an API correctly saves data to a database |
| System Testing | The complete application as a whole | Test an end-to-end e-commerce application |
| Acceptance Testing (UAT) | Whether software meets business and user requirements | Verify that a customer can place and track an order |

## 2. Functional Testing

Functional testing verifies **what the software does** against its specified requirements.

| Type | Purpose | Example |
|---|---|---|
| Smoke Testing | Checks whether the main features work after a new build | Verify that the application starts and login works |
| Sanity Testing | Quickly verifies a specific change or fix | Check a corrected payment calculation |
| Regression Testing | Ensures existing features still work after changes | Verify checkout after modifying the shopping cart |
| Retesting | Confirms that a previously reported defect has been fixed | Repeat the failed test after a bug fix |
| API Testing | Tests API endpoints, responses, status codes, and validation | Test `POST /orders` |
| UI Testing | Tests the user interface and user interactions | Verify form submission and error messages |
| End-to-End (E2E) Testing | Tests a complete business workflow across components | Login → add product → pay → receive confirmation |
| Exploratory Testing | Uses investigation and tester judgment to find unexpected defects | Try unusual sequences of user actions |
| Ad Hoc Testing | Informal testing without a predefined test case | Enter unexpected values to uncover a crash |

**Important distinction:** Retesting verifies a specific fix; regression testing checks whether other functionality has been affected.

## 3. Non-Functional Testing

Non-functional testing evaluates **how well the software works**, rather than only whether its features work.

| Type | Purpose | Example |
|---|---|---|
| Performance Testing | Measures speed, responsiveness, and resource usage | Measure API response time |
| Load Testing | Checks behavior under expected user traffic | Simulate 1,000 concurrent users |
| Stress Testing | Tests beyond normal operating capacity | Increase traffic until the application degrades |
| Spike Testing | Checks response to sudden traffic increases | Traffic jumps from 100 to 5,000 users |
| Endurance / Soak Testing | Checks stability over an extended period | Run a service continuously for 48 hours |
| Scalability Testing | Evaluates how the system handles increasing demand | Increase service instances as traffic grows |
| Security Testing | Identifies vulnerabilities and security weaknesses | Test authentication and authorization |
| Penetration Testing | Simulates attacks to discover exploitable weaknesses | Attempt to exploit an API vulnerability |
| Usability Testing | Evaluates ease of use | Observe users completing a purchase |
| Accessibility Testing | Checks usability for people with disabilities | Test keyboard navigation and screen-reader support |
| Compatibility Testing | Verifies operation across environments | Test browsers, operating systems, and devices |
| Reliability Testing | Checks consistent operation over time | Verify that a service runs without failures |
| Recovery Testing | Tests recovery after a failure | Restart a service after a database outage |
| Installation / Upgrade Testing | Checks installation, upgrades, and removal | Upgrade an application without losing configuration |
| Localization Testing | Verifies language and regional behavior | Test currency, date, and number formats |
| Portability Testing | Checks whether software can run in different environments | Move an application between supported operating systems |

## 4. Testing by Execution Method

| Type | Description | Typical tools or techniques |
|---|---|---|
| Manual Testing | A tester executes test cases manually | Test cases, checklists, Jira |
| Automated Testing | Scripts execute tests automatically | pytest, Selenium, Playwright |
| Static Testing | Examines code or documents without executing the program | Code reviews, linters, SonarQube |
| Dynamic Testing | Tests software by executing it | pytest, Postman |
| Black-Box Testing | Tests behavior without relying on internal implementation details | API and UI tests |
| White-Box Testing | Tests internal logic, paths, and code structure | Unit tests, code coverage tools |
| Gray-Box Testing | Tests behavior with partial knowledge of the internals | Database-aware integration tests |

## 5. Testing Across the SDLC

Testing starts before code is written and continues after deployment.

### Stage 1: Requirements and Design
- Requirements reviews
- Design reviews
- Test planning
- Acceptance-criteria validation
- Threat modeling

### Stage 2: Development
- Static analysis
- Unit testing
- Code reviews
- Component testing
- Developer tests

### Stage 3: Integration and Build
- Integration testing
- API testing
- Contract testing
- Smoke testing
- Build verification

### Stage 4: System and Release Validation
- System testing
- End-to-end testing
- Regression testing
- Performance testing
- Security testing
- Usability testing
- User Acceptance Testing (UAT)

### Stage 5: Deployment and Production
- Deployment verification
- Production smoke tests
- Canary validation
- Monitoring and alert checks
- Recovery testing
- Rollback testing

## 6. Specialized Testing in Modern Software Engineering

| Type | What it validates |
|---|---|
| Database Testing | Data integrity, constraints, queries, transactions, and migrations |
| Contract Testing | Whether communicating services follow agreed API contracts |
| Mutation Testing | Whether tests detect deliberately introduced code defects |
| Fuzz Testing | How software handles unexpected or malformed inputs |
| Chaos Testing | How systems behave when infrastructure or dependencies fail |
| Disaster Recovery Testing | Whether systems and data can be restored after a major incident |
| Data Quality Testing | Completeness, uniqueness, validity, and consistency of data |
| Migration Testing | Correctness of data and functionality after moving systems or platforms |
| Configuration Testing | Correct behavior under different configurations |
| Compliance Testing | Conformance to applicable standards and regulatory requirements |
| A/B Testing | Compares alternative implementations using real-user outcomes |
| AI/ML Model Testing | Evaluates predictive quality, robustness, bias, and model performance |
| LLM Application Testing | Evaluates factual correctness, hallucinations, relevance, safety, and tool use |
| MLOps Pipeline Testing | Validates data pipelines, model training, deployment, and reproducibility |

## 7. Common Testing Types in a CI/CD Pipeline

In modern DevOps, many tests run automatically whenever developers push code.

| Pipeline stage | Typical tests |
|---|---|
| Commit / pre-commit | Linting, static analysis, unit tests |
| Pull request | Unit, integration, contract, and code-quality checks |
| Build | Build verification, component tests, dependency and container scans |
| Staging | API, end-to-end, regression, performance, and security tests |
| Pre-release | Acceptance tests, smoke tests, release validation |
| Production | Health checks, synthetic monitoring, canary validation |

For example, a GitHub Actions pipeline could run unit tests using `pytest`, build a Docker or Podman image, execute integration tests, and block deployment if required checks fail.

## 8. Recommended Learning Order for a Practical Workshop

1. Unit testing with `pytest`
2. Integration testing with a database
3. API testing with FastAPI and Postman or pytest
4. Functional testing, regression testing, smoke testing, and retesting
5. UI automation with Playwright or Selenium
6. System and end-to-end testing
7. Performance testing with Locust or k6
8. Security testing and vulnerability scanning
9. CI/CD test automation with GitHub Actions
10. Production monitoring, reliability, and recovery testing

## Key Takeaway

- **Unit, integration, system, and acceptance testing** describe testing levels.
- **Functional, performance, and security testing** describe testing objectives.
- **Manual and automated testing** describe execution approaches.
- **Smoke, sanity, regression, and retesting** describe common testing activities.
- These categories overlap; they are not mutually exclusive. For example, an API test can be automated, functional, and part of integration testing.
