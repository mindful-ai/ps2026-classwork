# Terraform on AWS: Working EC2 Web Server Workshop

**Level:** Beginner\
**Platform:** Windows CMD / PowerShell\
**Cloud:** AWS\
**Region:** Mumbai (`ap-south-1`)\
**Project folder:** `terraform-web-demo`

## 1. Workshop objectives

By the end of this exercise, you will be able to:

-   Verify Terraform and AWS CLI installations.
-   Define AWS infrastructure in a Terraform configuration file.
-   Initialize and validate a Terraform project.
-   Preview infrastructure changes with `terraform plan`.
-   Create an EC2 instance and security group.
-   Test a simple web page hosted on the EC2 instance.
-   Inspect Terraform outputs and safely destroy the resources.

## 2. Architecture

Terraform will manage these resources:

1.  An AWS security group allowing inbound HTTP traffic on TCP port 80.
2.  One EC2 `t3.micro` instance running Amazon Linux 2023.
3.  A startup script that installs Python 3 and starts a basic HTTP
    server.
4.  Terraform outputs containing the instance ID, public IP, and website
    URL.

The example uses the default VPC in the selected AWS region. If your
account does not have a default VPC or usable subnets, see
Troubleshooting.

## 3. Important cost and security notes

-   AWS may charge for EC2 usage and related resources. Check current
    pricing and your account's Free Tier eligibility before proceeding.
-   Run `terraform destroy` after the workshop to remove the resources
    managed by this project.
-   The demo opens HTTP port 80 to the internet (`0.0.0.0/0`). Use this
    only for a temporary demonstration, not for sensitive or production
    applications.
-   The example serves plain HTTP, not HTTPS.
-   The instance needs outbound network access to install Python during
    startup.
-   Do not commit AWS access keys, secrets, Terraform state files, or
    other sensitive information to Git.
-   Terraform state records infrastructure details. Keep it private.

## 4. Prerequisites

Install and configure:

-   Terraform for Windows.
-   AWS CLI.
-   An AWS identity with permission to describe the required
    networking/AMI information and create, inspect, and delete EC2
    instances and security groups.
-   A working AWS region selection.

Open **CMD** and verify Terraform:

``` cmd
terraform -version
```

Verify AWS CLI:

``` cmd
aws --version
```

Verify AWS credentials:

``` cmd
aws sts get-caller-identity
```

Check that AWS has an availability zone in Mumbai:

``` cmd
aws ec2 describe-availability-zones --region ap-south-1 --query "AvailabilityZones[0].ZoneName" --output text
```

The identity command should return your AWS account and caller ARN. Do
not share credentials or secret access keys.

If `terraform` is not recognized, make sure the folder containing
`terraform.exe` is on your Windows `PATH`, then close and reopen CMD.

## 5. Create the project folder

Run these commands in CMD. If the folder already exists, skip `mkdir`
and enter the folder.

``` cmd
cd C:\Users\mindf\OneDrive\Projects\mindful-learning-academy\sapient-ai\classwork\day-12
mkdir terraform-web-demo
cd terraform-web-demo
```

Confirm your current directory:

``` cmd
cd
```

## 6. Create `main.tf`

Open Notepad:

``` cmd
notepad main.tf
```

Paste the following configuration and save the file.

``` hcl
terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 6.0"
    }
  }
}

provider "aws" {
  region = "ap-south-1"
}

# Find the default VPC in the selected region.
data "aws_vpc" "default" {
  default = true
}

# Find subnets that belong to the default VPC.
data "aws_subnets" "default" {
  filter {
    name   = "vpc-id"
    values = [data.aws_vpc.default.id]
  }
}

# Look up the current Amazon Linux 2023 AMI ID from SSM Parameter Store.
data "aws_ssm_parameter" "al2023" {
  name = "/aws/service/ami-amazon-linux-latest/al2023-ami-kernel-default-x86_64"
}

# Permit inbound HTTP traffic.
resource "aws_security_group" "web" {
  name        = "terraform-web-demo-sg"
  description = "Allow HTTP traffic for Terraform demo"
  vpc_id      = data.aws_vpc.default.id

  ingress {
    description = "HTTP"
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    description = "Allow outbound traffic"
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "terraform-web-demo-sg"
  }
}

# Create the EC2 instance.
resource "aws_instance" "web" {
  ami                         = data.aws_ssm_parameter.al2023.value
  instance_type               = "t3.micro"
  subnet_id                   = data.aws_subnets.default.ids[0]
  associate_public_ip_address = true

  vpc_security_group_ids = [
    aws_security_group.web.id
  ]

  # This script runs when the instance first boots.
  user_data = <<-EOF
    #!/bin/bash
    set -eux
    dnf install -y python3
    mkdir -p /var/www/demo
    echo '<h1>Terraform deployment successful!</h1><p>Running on AWS EC2.</p>' > /var/www/demo/index.html
    cd /var/www/demo
    nohup python3 -m http.server 80 --bind 0.0.0.0 > /var/log/demo-web.log 2>&1 &
  EOF

  tags = {
    Name = "terraform-web-demo"
  }
}

output "instance_id" {
  description = "ID of the demo EC2 instance"
  value       = aws_instance.web.id
}

output "public_ip" {
  description = "Public IPv4 address of the demo EC2 instance"
  value       = aws_instance.web.public_ip
}

output "website_url" {
  description = "URL of the demo website"
  value       = "http://${aws_instance.web.public_ip}"
}
```

### How the configuration works

  -----------------------------------------------------------------------
  Terraform element                   Purpose
  ----------------------------------- -----------------------------------
  `terraform` block                   Declares provider requirements

  `provider "aws"`                    Selects AWS and the Mumbai region

  `data "aws_vpc"`                    Reads the default VPC; does not
                                      create it

  `data "aws_subnets"`                Reads subnets in that VPC

  `data "aws_ssm_parameter"`          Retrieves the current Amazon Linux
                                      2023 AMI ID

  `resource "aws_security_group"`     Creates the firewall rules for the
                                      demo

  `resource "aws_instance"`           Creates the virtual machine

  `user_data`                         Runs setup commands during first
                                      boot

  `output` blocks                     Display useful values after
                                      deployment
  -----------------------------------------------------------------------

## 7. Initialize the project

Run:

``` cmd
terraform init
```

Terraform downloads the AWS provider and prepares the working directory.
A `.terraform` directory and a dependency lock file are created.

## 8. Format and validate the configuration

Run each command:

``` cmd
terraform fmt
terraform validate
```

Expected validation result:

``` text
Success! The configuration is valid.
```

If validation fails, fix the reported error before continuing.

## 9. Preview the changes

Run:

``` cmd
terraform plan
```

Review the plan before creating resources. The first deployment should
propose creating a security group and an EC2 instance. The VPC, subnet,
and AMI are data lookups, not resources created by this configuration.

If the plan fails because the default VPC or subnets do not exist, see
Troubleshooting.

## 10. Create the infrastructure

Only after reviewing the plan, run:

``` cmd
terraform apply
```

Review the plan shown by Terraform. Type `yes` when prompted to approve
the changes.

Wait for Terraform to finish. The EC2 instance may need another minute
or two after creation for its startup script to finish.

## 11. Get the website URL

Run:

``` cmd
terraform output
```

Or print only the URL:

``` cmd
terraform output website_url
```

Open the printed URL in a browser. It should display:

**Terraform deployment successful!**

You can also test from CMD:

``` cmd
curl http://PUBLIC_IP
```

Replace `PUBLIC_IP` with the IP printed by `terraform output public_ip`.

If the page does not load immediately, wait briefly and try again. If it
still fails, use the troubleshooting steps below.

## 12. Verify the instance in AWS

You can inspect the instance in the AWS Console:

1.  Select the Mumbai region (`ap-south-1`).
2.  Open **EC2 → Instances**.
3.  Find the instance tagged `terraform-web-demo`.
4.  Confirm the instance is running and has a public IPv4 address.

The AWS Console is useful for observation, but use Terraform for changes
to resources managed by this project.

## 13. Experiment: change the instance type

Open `main.tf` and change:

``` hcl
instance_type = "t3.micro"
```

to another instance type available to your account and region. Check its
cost before using it.

Then run:

``` cmd
terraform fmt
terraform plan
```

Review the proposed changes. If you want to apply them, run:

``` cmd
terraform apply
```

This demonstrates the Terraform workflow: edit configuration, inspect
the plan, and apply only after review. Changing an EC2 instance type may
cause Terraform to stop, modify, or replace the instance depending on
the change and provider behavior.

For the next experiment, change the HTML text in the `user_data` script.
Note that changing user data does not automatically mean the startup
script will rerun on an already-running instance. For a repeatable
update workflow, use a configuration-management or deployment step, or
deliberately replace the instance in a separate exercise.

## 14. Destroy the resources

When you have finished testing, run:

``` cmd
terraform destroy
```

Review the proposed deletions and type `yes` to confirm.

Terraform should delete the EC2 instance and security group managed by
this project. The default VPC and subnets were only read, so Terraform
will not delete them.

Verify the state:

``` cmd
terraform state list
```

After a successful destroy, the managed resources should no longer be
listed.

## 15. Useful Terraform commands

  Command                  Purpose
  ------------------------ -----------------------------------------------
  `terraform -version`     Show installed Terraform version
  `terraform init`         Initialize the working directory
  `terraform fmt`          Format Terraform files
  `terraform validate`     Check configuration syntax and consistency
  `terraform plan`         Preview proposed infrastructure changes
  `terraform apply`        Apply the configuration
  `terraform output`       Display output values
  `terraform state list`   List resources tracked in state
  `terraform destroy`      Delete resources managed by the configuration

## 16. Troubleshooting

### A. `terraform` is not recognized

Check:

``` cmd
where terraform
terraform -version
```

If needed, add the directory containing `terraform.exe` to the user
`Path` environment variable, then reopen the terminal.

### B. AWS credentials or permissions fail

Run:

``` cmd
aws sts get-caller-identity
```

If this fails, configure AWS CLI credentials or your organization's
approved authentication method. If identity works but Terraform receives
`AccessDenied`, the AWS identity needs the required permissions.

### C. Default VPC or subnet not found

This configuration expects a default VPC and at least one subnet in
Mumbai. Check:

``` cmd
aws ec2 describe-vpcs --region ap-south-1 --filters Name=isDefault,Values=true
aws ec2 describe-subnets --region ap-south-1
```

If your account does not have a default VPC, create or select an
appropriate VPC and subnet, then update the configuration. Do not delete
or recreate shared networking resources without checking their use.

### D. Website URL times out

Check that:

-   The EC2 instance is running.
-   The instance has a public IPv4 address.
-   The subnet's route table provides a route to an internet gateway.
-   The security group permits inbound TCP port 80.
-   The instance can reach the internet to install Python.
-   The startup script completed successfully.

The instance is not configured with SSH access. To inspect startup logs,
use an approved method such as EC2 console system logs or AWS Systems
Manager if the instance has been configured for it. The user-data log is
commonly available at `/var/log/cloud-init-output.log` on Amazon Linux.

### E. A resource name already exists

The security group name `terraform-web-demo-sg` must be unique within
the VPC. If it already exists, choose a different name in `main.tf`,
then run `terraform plan` again.

### F. `terraform destroy` fails

Read the error carefully. Resources may have been changed outside
Terraform or may have dependencies. Do not manually delete resources
blindly. Inspect the Terraform state and AWS Console, then reconcile the
configuration and state safely.

## 17. Workshop completion checklist

-   [ ] Terraform and AWS CLI are installed.
-   [ ] AWS identity check succeeds.
-   [ ] `terraform init` succeeds.
-   [ ] `terraform fmt` and `terraform validate` succeed.
-   [ ] `terraform plan` reviewed.
-   [ ] EC2 instance and security group created.
-   [ ] Website opened successfully.
-   [ ] Terraform outputs inspected.
-   [ ] `terraform destroy` completed.
-   [ ] No workshop resources remain running.

## 18. Further exercises

1.  Add an output for the EC2 instance availability zone.
2.  Add a `Name` tag and another custom tag.
3.  Change the page content and discuss how instance user data behaves.
4.  Restrict HTTP access to a known client IP for a private
    demonstration.
5.  Create a second instance and compare the plan.
6.  Store the configuration in Git while excluding Terraform state and
    secrets.
7.  Run `terraform plan` in a CI workflow and require approval before
    `terraform apply`.

------------------------------------------------------------------------

**End of workshop.** Always review the plan before applying changes, and
destroy temporary resources after testing.
