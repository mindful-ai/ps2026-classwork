# AWS IAM (Identity and Access Management) – Workshop Manual

---

## 1. Service Overview
AWS Identity and Access Management (IAM) enables you to **securely control access** to AWS services and resources.  
It lets you manage:
- **Users**: Individual accounts with credentials.  
- **Groups**: Collection of users with common permissions.  
- **Roles**: Temporary credentials for AWS services or cross-account access.  
- **Policies**: JSON-based permission definitions attached to users, groups, or roles.  

IAM is a **foundational service** for AWS security and applies across all AWS accounts.  

---

## 2. Key Features & Use Cases

### Features
- **Granular permissions**: Assign least-privilege access.  
- **Multi-factor authentication (MFA)** support.  
- **Federated access**: Integrate with corporate directories (AD/SSO).  
- **Cross-account access** with IAM roles.  
- **Auditability**: Track access using AWS CloudTrail logs.  

### Use Cases
1. **Create separate accounts for developers** instead of sharing root credentials.  
2. **Grant temporary access** to third-party vendors.  
3. **Assign roles to EC2 instances** for securely accessing S3 buckets without embedding credentials.  
4. **Enforce MFA** for critical administrative users.  

---

## 3. Practical Example (AWS Free Tier)

### Objective
Create an IAM **user with restricted permissions** (e.g., S3 read-only access) and test login.  

### Services Used
- **IAM**  
- **S3 (for testing access)**  

---

## 4. Step-by-Step Hands-On

### Step 1: Access IAM Console
1. Log in to the AWS Management Console with your **root account** (not recommended for daily use).  
2. Navigate to **IAM** service.  

---

### Step 2: Create a User
1. In the IAM dashboard, click **Users → Add user**.  
2. Enter username: `test-user`.  
3. Select **Access type**:  
   - ✅ AWS Management Console access.  
   - Optionally set a custom password.  
4. Click **Next**.  

---

### Step 3: Assign Permissions
1. Choose **Attach policies directly**.  
2. Search for **AmazonS3ReadOnlyAccess**.  
3. Select it and continue.  

---

### Step 4: Review and Create User
1. Review configuration.  
2. Click **Create user**.  

---

### Step 5: Test User Access
1. Log out from the root account.  
2. Sign in again using the IAM user:  
   - Login URL: shown in IAM dashboard under **IAM user sign-in link**.  
   - Username: `test-user`.  
   - Password: (set during creation).  
3. Navigate to **S3 service**:  
   - The user should see available buckets.  
   - Try uploading a file → It should fail (read-only access).  

---

### Step 6: Best Practices
- Always create **individual IAM users** (never share root credentials).  
- Apply **least privilege principle**.  
- Enable **MFA for all admin accounts**.  
- Use **IAM roles** instead of embedding access keys in applications.  

---

## 5. Summary
- IAM secures access across AWS services.  
- Users, groups, roles, and policies provide flexible access management.  
- In this exercise, you created a **read-only IAM user for S3**, tested login, and verified permissions.  

✅ You now understand how IAM helps enforce **secure and controlled access** to AWS resources.  

---
