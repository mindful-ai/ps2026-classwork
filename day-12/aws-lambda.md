# AWS Lambda – Workshop Manual

## 1. Service Overview
AWS Lambda is a **serverless compute service** that lets you run code without managing servers.  
You upload your function code, and AWS executes it **on demand** in response to events (like S3 uploads, API Gateway requests, or DynamoDB updates).

---

## 2. Key Features
- **No servers to manage** – fully managed by AWS.  
- **Event-driven** – triggers from 200+ AWS and external services.  
- **Automatic scaling** – runs as many instances as needed.  
- **Pay-per-use** – charged only for execution time.  
- **Multi-language support** – Python, Node.js, Java, Go, C#, Ruby, etc.  

---

## 3. Common Use Cases
- Responding to S3 file uploads (e.g., resize an image).  
- Backend APIs (with API Gateway + Lambda).  
- Automating scheduled tasks (CloudWatch Events).  
- Real-time log/data processing.  
- Chatbots, IoT backends, or microservices.  

---

## 4. Hands-On Example (Free Tier)

### Goal
Create a Lambda function in Python that returns `"Hello from Lambda!"`.

---

### Step 1: Create Function
1. Go to **AWS Console → Lambda**.  
2. Click **Create function**.  
3. Choose **Author from scratch**.  
4. Function name: `helloLambda`.  
5. Runtime: **Python 3.x**.  
6. Leave defaults → Click **Create function**.  

---

### Step 2: Add Code
In the inline editor, replace default code with:

```python
def lambda_handler(event, context):
    return {
        "statusCode": 200,
        "body": "Hello from Lambda!"
    }
```

Click **Deploy**.

---

### Step 3: Test the Function
1. Click **Test**.  
2. Create a test event (any dummy JSON, e.g., `{}`).  
3. Run test → You should see:

```json
{
  "statusCode": 200,
  "body": "Hello from Lambda!"
}
```

---

### Step 4 (Optional): Trigger via API Gateway
1. Add **API Gateway trigger** from the Lambda console.  
2. Choose **REST API → Open**.  
3. Deploy → Copy the API endpoint.  
4. Open endpoint in browser → It should return `"Hello from Lambda!"`.

---

## 5. Best Practices
- Keep functions **small and focused** (single responsibility).  
- Use **environment variables** for configs.  
- Use **IAM roles** instead of hardcoding credentials.  
- Monitor with **CloudWatch Logs** and **X-Ray tracing**.  
- Avoid large deployment packages (>50MB); use **Lambda Layers**.  

---

## 6. Summary
- Lambda is **serverless compute** – no servers to manage.  
- It runs code **on demand, event-driven, and auto-scales**.  
- Hands-on: created a Python Lambda, tested it, and learned best practices.  

---
