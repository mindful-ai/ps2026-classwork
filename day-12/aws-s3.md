# AWS S3 (Simple Storage Service) – Workshop Manual

---

## 1. Service Overview
Amazon S3 is an **object storage service** designed to store and retrieve any amount of data, from anywhere, at any time.  
It is durable, scalable, and cost-effective, making it the backbone for many AWS applications.

---

## 2. Key Features & Use Cases

### Features
- Store **unlimited data** in buckets (containers).  
- 99.999999999% durability (11 nines).  
- Lifecycle management (move data to cheaper storage tiers automatically).  
- Versioning for data protection.  
- Integration with almost every AWS service.  

### Use Cases
- Data lake for analytics.  
- Backup and archiving.  
- Hosting static websites.  
- Storing ML training datasets.  

---

## 3. Practical Example (AWS Free Tier)
Create a bucket, upload a file, and enable public access for static hosting.

---

## 4. Step-by-Step Hands-On

### Step 1: Create a Bucket
1. Go to **S3 service** in AWS console.  
2. Click **Create bucket**.  
3. Name it: `my-demo-bucket-[uniqueid]`.  
4. Choose Region (e.g., `us-east-1`).  
5. Keep default settings and click **Create bucket**.  

### Step 2: Upload a File
1. Open the bucket.  
2. Click **Upload → Add files**.  
3. Upload a sample `.txt` file.  

### Step 3: Test Access
1. Click on the file → Copy **Object URL**.  
2. Try to open in browser: access denied (default secure).  

### Step 4: Enable Public Access (for demo only)
1. In bucket → **Permissions → Block Public Access → Uncheck** (confirm).  
2. Go back to file → **Make public**.  
3. Open Object URL in browser → File should display.  

---

## 5. Best Practices
- Never make sensitive buckets public.  
- Use bucket policies and IAM for access control.  
- Enable versioning and MFA delete for critical data.  

---

## 6. Summary
- S3 is AWS’s most widely used storage service.  
- Ideal for backups, data lakes, and web hosting.  
- Hands-on: created a bucket, uploaded file, and tested access.  

---
