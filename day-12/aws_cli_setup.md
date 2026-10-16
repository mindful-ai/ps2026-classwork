# AWS CLI Setup Guide

This guide walks you through installing, configuring, and testing the AWS CLI (v2).

---

## 1. Pre-requisites
- An AWS account.
- Either:
  - IAM user with **programmatic access** (Access Key ID + Secret Access Key), or
  - IAM Identity Center (SSO) credentials.

> ⚠️ Avoid using root account credentials.

---

## 2. Install AWS CLI v2

### Linux
```bash
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip
sudo ./aws/install
aws --version
```

### macOS (pkg)
```bash
curl "https://awscli.amazonaws.com/AWSCLIV2.pkg" -o "AWSCLIV2.pkg"
sudo installer -pkg AWSCLIV2.pkg -target /
aws --version
```

Or via Homebrew:
```bash
brew install awscli
aws --version
```

### Windows (MSI)
1. Download [AWS CLI MSI installer](https://awscli.amazonaws.com/AWSCLIV2.msi).
2. Run the installer and open **PowerShell**:
```powershell
aws --version
```

---

## 3. Configure AWS CLI

Run:
```bash
aws configure
```
Prompts:
- **AWS Access Key ID** → Your IAM user access key ID.  
- **AWS Secret Access Key** → Your secret key.  
- **Default region name** → e.g., `us-east-1`.  
- **Default output format** → `json`, `table`, or `text`.  

Configuration files:
- `~/.aws/credentials` → stores keys.
- `~/.aws/config` → stores region/output format.

### Example (`~/.aws/credentials`):
```
[default]
aws_access_key_id = AKIAIOSFODNN7EXAMPLE
aws_secret_access_key = wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY
```

### Example (`~/.aws/config`):
```
[default]
region = us-east-1
output = json
```

---

## 4. Test Your Setup

Check identity:
```bash
aws sts get-caller-identity
```

List S3 buckets:
```bash
aws s3 ls
```

Upload file to S3:
```bash
aws s3 cp ./file.txt s3://my-bucket-name/file.txt
```

---

## 5. Optional: SSO Setup
If your organization uses IAM Identity Center:
```bash
aws configure sso
aws sso login --profile my-sso-profile
```

---

## 6. Notes & Best Practices
- Use **named profiles** for multiple accounts (`aws configure --profile myprofile`).  
- Avoid embedding credentials in scripts. Use IAM roles or SSO.  
- To switch profiles:  
```bash
aws s3 ls --profile myprofile
```

---

✅ You’re now ready to use AWS CLI!
