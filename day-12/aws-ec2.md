# AWS EC2 (Elastic Compute Cloud) – Workshop Manual

---

## 1. Service Overview
Amazon EC2 provides **resizable compute capacity in the cloud**.  
It allows you to launch virtual servers (instances) with different OS, CPU, memory, and storage configurations.

---

## 2. Key Features & Use Cases

### Features
- Choose from 500+ instance types (general, compute, GPU, memory optimized).  
- Auto-scaling and load balancing.  
- Pay only for usage.  
- Integration with EBS (block storage).  

### Use Cases
- Web application hosting.  
- Running development/test environments.  
- Big data processing.  
- ML training on GPU instances.  

---

## 3. Practical Example (AWS Free Tier)
Launch a free-tier EC2 instance, connect, and install Apache web server.

---

## 4. Step-by-Step Hands-On

### Step 1: Launch Instance
1. Open **EC2 service**.  
2. Click **Launch instance**.  
3. Name: `my-ec2-demo`.  
4. Choose **Amazon Linux 2 (Free Tier eligible)**.  
5. Instance type: **t2.micro**.  
6. Create new key pair (download `.pem` file).  
7. Configure security group → allow **SSH (22)** and **HTTP (80)**.  
8. Launch instance.  

### Step 2: Connect via SSH
1. Open terminal/PowerShell.  
2. Run:  
   ```bash
   ssh -i my-key.pem ec2-user@<public-ip>
    ```

### Step 3: Install Apache

Inside EC2 terminal:

```bash
sudo yum update -y
sudo yum install httpd -y
sudo systemctl start httpd
echo "Hello from EC2" | sudo tee /var/www/html/index.html
```

### Step 4: Test Web Server

Copy public IP → Open in browser → Should show “Hello from EC2”.

### 5. Best Practices

-   Never use root account for SSH.
-   Always restrict security groups to trusted IPs.
-   Stop/terminate unused instances to save cost.

### 6. Summary

- EC2 provides cloud-based virtual machines.
- Flexible for hosting, dev, and ML workloads.
- Hands-on: launched an instance, connected, deployed a web server.