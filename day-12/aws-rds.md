
---

# **AWS RDS (Relational Database Service) – Workshop Manual**

```markdown
# AWS RDS (Relational Database Service) – Workshop Manual

---

## 1. Service Overview
Amazon RDS is a **managed relational database service**.  
It supports popular databases (MySQL, PostgreSQL, Oracle, SQL Server, MariaDB, Aurora).  
AWS manages backups, patching, scaling, and high availability.

---

## 2. Key Features & Use Cases

### Features
- Automated backups & snapshots.  
- Multi-AZ deployments for HA.  
- Read replicas for scaling reads.  
- Integration with IAM & VPC security.  

### Use Cases
- Web application backends.  
- Business applications needing SQL.  
- Analytics on structured data.  

---

## 3. Practical Example (AWS Free Tier)
Launch a free-tier MySQL RDS instance and connect via MySQL client.

---

## 4. Step-by-Step Hands-On

### Step 1: Launch RDS Instance
1. Go to **RDS service**.  
2. Click **Create database**.  
3. Choose **Standard Create**.  
4. Engine: **MySQL** (free tier eligible).  
5. Version: select latest free-tier supported.  
6. Templates: **Free tier**.  
7. DB instance identifier: `myrdsdemo`.  
8. Master username/password: set values.  
9. Storage: default (20GB).  
10. Connectivity: Allow public access (demo only).  

### Step 2: Connect from EC2
1. Launch an EC2 instance (as in previous manual).  
2. Install MySQL client:  
   ```bash
   sudo yum install mysql -y
3. Connect to RDS
    ```bash
    mysql -h <RDS-endpoint> -u <username> -p
4. Create a table
    ```sql
    CREATE DATABASE demo;
    USE demo;
    CREATE TABLE users (id INT PRIMARY KEY, name VARCHAR(50));
    INSERT INTO users VALUES (1, 'Alice'), (2, 'Bob');
    SELECT * FROM users;


### Best Practices

- Do not allow public access in production.
- Use IAM authentication where possible.
- Enable automated backups and multi-AZ for resilience.

### Summary

- RDS simplifies relational database management.
- Supports multiple popular engines.
- Hands-on: launched MySQL RDS, connected via EC2, ran queries.

