## Prepare your EC2 instance

#### Update packages
sudo apt update && sudo apt upgrade -y

#### Install Docker
sudo apt install docker.io -y
sudo usermod -aG docker $USER
newgrp docker

#### Install Git and clone your repository
sudo apt install git -y
cd ~
git clone https://github.com/YOUR_USERNAME/YOUR_REPO.git
cd YOUR_REPO

## Add application Dockerfile

```bash
FROM python:3.11-slim

WORKDIR /app

COPY ./requirements.txt /app/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /app/requirements.txt

COPY . /app

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```


## Save Repository Secrets in GitHub

Go to your repository on GitHub, navigate to Settings > Secrets and variables > Actions, and add the following repository secrets:

• EC2_HOST: The Public IPv4 address or DNS of your EC2 instance.
• EC2_USERNAME: The login user (usually ubuntu for Ubuntu instances).
• EC2_SSH_KEY: The entire text contents of your private .pem key file.

## Create the GitHub Actions Workflow

```yml
name: Deploy FastAPI to EC2

on:
  push:
    branches:
      - main  # Triggers deployment whenever you push to main

jobs:
  deploy:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout repository code
        uses: actions/checkout@v4

      - name: SSH into EC2 and Deploy
        uses: appleboy/ssh-action@v1.0.3
        with:
          host: ${{ secrets.EC2_HOST }}
          username: ${{ secrets.EC2_USERNAME }}
          key: ${{ secrets.EC2_SSH_KEY }}
          script: |
            # Navigate to application folder
            cd ~/YOUR_REPO
            
            # Pull latest changes from GitHub
            git pull origin main
            
            # Build the new Docker image
            docker build -t fastapi-app .
            
            # Stop and remove the old container if it exists
            docker stop fastapi-container || true
            docker rm fastapi-container || true
            
            # Run the new container
            docker run -d \
              --name fastapi-container \
              -p 8000:8000 \
              --restart always \
              fastapi-app


```

Commit and push this workflow to your main branch. Head to the Actions tab of your repository to view the live build status

Your output should be available on 
http://<public-ip-of-ec2>:8000/docs