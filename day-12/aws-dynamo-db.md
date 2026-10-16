# AWS DynamoDB – Workshop Manual

## 1. Service Overview
Amazon DynamoDB is a **fully managed NoSQL database service** that provides:
- **Key-Value & Document store**.  
- **Single-digit millisecond performance** at any scale.  
- **Serverless** – no infrastructure to manage.  
- **Automatic scaling** and high availability.  

---

## 2. Key Features
- **NoSQL (non-relational)** storage – flexible schema.  
- **Primary key** (partition key or partition + sort key).  
- **On-demand or provisioned capacity**.  
- **Global Tables** – multi-region replication.  
- **Streams** – capture real-time item-level changes.  
- **Integration with Lambda, API Gateway, S3, and more**.  

---

## 3. Common Use Cases
- Real-time applications (gaming leaderboards, chat apps).  
- IoT data storage.  
- E-commerce shopping carts.  
- Serverless web applications.  
- Logging and event tracking.  

---

## 4. Hands-On Example (AWS Free Tier)

### Goal
Create a DynamoDB table and insert + read items.

---

### Step 1: Create a Table
1. Go to **AWS Console → DynamoDB**.  
2. Click **Create Table**.  
3. Table name: `CustomerTable`.  
4. Partition key: `CustomerID` (String).  
5. Leave other defaults → Click **Create**.  

---

### Step 2: Insert an Item
1. Open the `CustomerTable`.  
2. Click **Explore table items → Create item**.  
3. Add JSON data:

```json
{
  "CustomerID": "CUST1001",
  "Name": "Alice Johnson",
  "Email": "alice@example.com",
  "Membership": "Gold"
}
```
aws 
### Step 3: Query the Table

- Go to Explore table items.
- Search with CustomerID = CUST1001.
- You should see Alice’s record.