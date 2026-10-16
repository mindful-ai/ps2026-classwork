# AWS Basics and Core Services

This workshop introduces professionals to **Amazon Web Services (AWS)**, covering fundamental concepts, architecture, and frequently used services across compute, storage, networking, and databases.  

---

# Part 1: Introduction to AWS

- AWS (Amazon Web Services) is the **leading cloud service provider**, offering 200+ fully managed services.  
- Customers range from startups to enterprises across industries.  
- Key advantages:  
  - On-demand scalability.  
  - Pay-as-you-go pricing.  
  - Global reach with data centers (Regions & Availability Zones).  
  - Security and compliance at scale.  

---

# Part 2: AWS Global Infrastructure

- **Regions**: Geographical locations where AWS has data centers (e.g., US-East-1, ap-south-1).  
- **Availability Zones (AZs)**: Physically separated data centers within a region.  
- **Edge Locations**: Content delivery endpoints via Amazon CloudFront.  
- **Shared Responsibility Model**:  
  - AWS manages the infrastructure security.  
  - Customers secure data, applications, and access control.  

---

# Part 3: Compute Services

## 3.1 Amazon EC2 (Elastic Compute Cloud)
- Virtual servers in the cloud.  
- Different instance types for general purpose, compute-optimized, GPU, and memory-optimized workloads.  
- Supports auto-scaling and load balancing.  

## 3.2 AWS Lambda
- Serverless compute – run code without managing servers.  
- Event-driven (e.g., triggered by S3 upload, API call).  
- Pay only for execution time.  

## 3.3 Amazon ECS & EKS
- ECS: Elastic Container Service for Docker workloads.  
- EKS: Elastic Kubernetes Service for Kubernetes orchestration.  

## 3.4 Elastic Beanstalk
- PaaS for deploying applications with minimal configuration.  

---

# Part 4: Storage Services

## 4.1 Amazon S3 (Simple Storage Service)
- Object storage for structured, semi-structured, and unstructured data.  
- Features: versioning, lifecycle policies, cross-region replication.  
- Used for backups, data lakes, and static website hosting.  

## 4.2 Amazon EBS (Elastic Block Store)
- Block storage for EC2 instances (similar to virtual hard drives).  

## 4.3 Amazon EFS (Elastic File System)
- Scalable, shared file storage accessible across multiple instances.  

## 4.4 AWS Glacier
- Low-cost archival storage for long-term backups.  

---

# Part 5: Databases in AWS

## 5.1 Amazon RDS (Relational Database Service)
- Managed relational databases: MySQL, PostgreSQL, Oracle, SQL Server, MariaDB, Aurora.  
- Automated backups, scaling, and patching.  

## 5.2 Amazon DynamoDB
- Fully managed NoSQL database.  
- High performance, serverless, auto-scaling.  

## 5.3 Amazon Redshift
- Data warehouse for large-scale analytics.  
- Columnar storage and massively parallel processing.  

---

# Part 6: Networking and Content Delivery

## 6.1 Amazon VPC (Virtual Private Cloud)
- Isolated network in the cloud.  
- Control over IP ranges, subnets, route tables, gateways.  

## 6.2 Elastic Load Balancer (ELB)
- Distributes incoming traffic across multiple instances.  

## 6.3 Amazon CloudFront
- Content Delivery Network (CDN) for global distribution.  
- Caches content at edge locations.  

## 6.4 Route 53
- Managed DNS service for domain name resolution and routing.  

---

# Part 7: Security and Identity

## 7.1 IAM (Identity and Access Management)
- Manage users, groups, and roles.  
- Define fine-grained permissions with policies.  
- Enable MFA for secure access.  

## 7.2 AWS KMS (Key Management Service)
- Create and manage encryption keys.  

## 7.3 AWS CloudTrail
- Logs API calls for auditing and compliance.  

---

# Part 8: Monitoring and Management

- **Amazon CloudWatch**: Metrics, logs, alarms for applications and infrastructure.  
- **AWS Config**: Track resource configurations and compliance.  
- **AWS Trusted Advisor**: Recommendations for cost optimization, performance, security, and fault tolerance.  

---

# Part 9: Pricing and Billing

- **Pay-as-you-go** model.  
- **Free Tier**: 12-month free usage for many services (e.g., EC2, S3, Lambda).  
- **Pricing Tools**:  
  - AWS Pricing Calculator.  
  - Cost Explorer for tracking usage and costs.  

---

# Part 10: Key Takeaways

- AWS provides **building blocks** for compute, storage, networking, and databases.  
- Services are **modular and integrated**, enabling flexible solutions.  
- Professionals must understand **core services first** before diving into advanced AI/ML workloads.  
- Hands-on with AWS console is critical for real learning.  

---

