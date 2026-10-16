# AWS CLI – Frequently Used Commands Cheatsheet

## 🔧 General / Setup
```bash
aws configure                # Configure credentials, region, output format
aws configure list           # Show current config
aws sts get-caller-identity  # Show current user/account details
aws help                     # General AWS CLI help
```

---

## ☁️ S3 (Storage)
```bash
aws s3 ls                                # List all buckets
aws s3 ls s3://my-bucket                 # List contents of a bucket
aws s3 mb s3://my-new-bucket             # Create a new bucket
aws s3 cp file.txt s3://my-bucket/       # Upload file to bucket
aws s3 cp s3://my-bucket/file.txt .      # Download file from bucket
aws s3 sync ./localdir s3://my-bucket/   # Sync local folder to bucket
aws s3 rm s3://my-bucket/file.txt        # Delete file from bucket
```

---

## 💻 EC2 (Compute)
```bash
aws ec2 describe-instances                # List all EC2 instances
aws ec2 describe-instances --query "Reservations[*].Instances[*].[InstanceId,State.Name,PublicIpAddress]" --output table
aws ec2 start-instances --instance-ids i-1234567890abcdef0   # Start instance
aws ec2 stop-instances --instance-ids i-1234567890abcdef0    # Stop instance
aws ec2 reboot-instances --instance-ids i-1234567890abcdef0  # Reboot instance
aws ec2 terminate-instances --instance-ids i-1234567890abcdef0 # Terminate instance
aws ec2 describe-key-pairs               # List key pairs
aws ec2 describe-security-groups         # List security groups
```

---

## 👤 IAM (Identity & Access Management)
```bash
aws iam list-users                       # List all users
aws iam get-user                         # Get details of current user
aws iam list-groups                      # List groups
aws iam list-roles                       # List IAM roles
aws iam list-policies                    # List IAM policies
```

---

## 🛠️ CloudFormation
```bash
aws cloudformation list-stacks           # List all stacks
aws cloudformation describe-stacks       # Describe stacks
aws cloudformation create-stack --stack-name my-stack --template-body file://template.yaml
aws cloudformation delete-stack --stack-name my-stack
```

---

## 🔑 Secrets Manager
```bash
aws secretsmanager list-secrets          # List secrets
aws secretsmanager get-secret-value --secret-id MySecret
```

---

## 📊 CloudWatch
```bash
aws cloudwatch list-metrics              # List available metrics
aws cloudwatch get-metric-statistics --namespace AWS/EC2 --metric-name CPUUtilization --dimensions Name=InstanceId,Value=i-1234567890abcdef0 --start-time 2025-09-01T00:00:00Z --end-time 2025-09-10T00:00:00Z --period 3600 --statistics Average
```

---

## 📦 ECR (Elastic Container Registry)
```bash
aws ecr describe-repositories            # List repositories
aws ecr create-repository --repository-name my-repo
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin <account_id>.dkr.ecr.us-east-1.amazonaws.com
```

---

## 🚀 ECS (Elastic Container Service)
```bash
aws ecs list-clusters                    # List clusters
aws ecs list-services --cluster my-cluster
aws ecs list-tasks --cluster my-cluster
```

---

## 🐳 EKS (Kubernetes)
```bash
aws eks list-clusters                    # List EKS clusters
aws eks describe-cluster --name my-cluster
```

---

## 📡 Lambda
```bash
aws lambda list-functions                # List Lambda functions
aws lambda invoke --function-name MyFunction output.json
aws lambda update-function-code --function-name MyFunction --zip-file fileb://function.zip
```

---

## 🔄 API Gateway
```bash
aws apigateway get-rest-apis             # List APIs
aws apigateway get-resources --rest-api-id <api_id>
```

---

## 🔒 KMS (Encryption Keys)
```bash
aws kms list-keys                        # List keys
aws kms describe-key --key-id <key-id>
```

---

## 🗄️ DynamoDB
```bash
aws dynamodb list-tables                 # List tables
aws dynamodb describe-table --table-name MyTable
aws dynamodb scan --table-name MyTable
aws dynamodb put-item --table-name MyTable --item '{"id":{"S":"1"},"name":{"S":"Alice"}}'
```

---

## 📥 SQS (Queues)
```bash
aws sqs list-queues                      # List queues
aws sqs create-queue --queue-name my-queue
aws sqs send-message --queue-url <queue_url> --message-body "Hello from AWS CLI"
aws sqs receive-message --queue-url <queue_url>
```

---

## 📢 SNS (Notifications)
```bash
aws sns list-topics                      # List topics
aws sns create-topic --name my-topic
aws sns publish --topic-arn <topic_arn> --message "Hello from AWS CLI"
```

---

## 🔑 RDS (Relational Database Service)
```bash
aws rds describe-db-instances            # List RDS instances
aws rds start-db-instance --db-instance-identifier mydb
aws rds stop-db-instance --db-instance-identifier mydb
```

---

## 🌍 Route 53
```bash
aws route53 list-hosted-zones            # List hosted zones
aws route53 list-resource-record-sets --hosted-zone-id <zone_id>
```

---

## 🚦 VPC & Networking
```bash
aws ec2 describe-vpcs                    # List VPCs
aws ec2 describe-subnets                 # List subnets
aws ec2 describe-route-tables            # List route tables
aws ec2 describe-internet-gateways       # List internet gateways
```
