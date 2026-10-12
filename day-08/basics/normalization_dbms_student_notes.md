# Normalization in DBMS — Student Notes

## 1. What is Normalization?

**Normalization is the process of organizing data in a relational database into well-structured tables to reduce unnecessary data duplication and prevent data anomalies.**

The main objectives are:

- Reduce data redundancy.
- Maintain data consistency.
- Avoid insertion, update and deletion anomalies.
- Establish clear relationships between tables.

**Example scenario:** An e-commerce company stores customer details, order information and product details in a single table. Whenever a customer places multiple orders, their name and address are repeated. Normalization helps organize this data into related tables.

## 2. Why do we need Normalization?

Consider the following table.

### Unnormalized design

| Order ID | Customer | City | Product | Price |
|---|---|---|---|---:|
| 101 | Ananya | Bengaluru | Laptop | 50000 |
| 101 | Ananya | Bengaluru | Mouse | 800 |
| 102 | Rahul | Mysuru | Keyboard | 1500 |
| 103 | Ananya | Bengaluru | Monitor | 12000 |

Notice that Ananya's details are repeated three times.

This can cause three types of anomalies:

| Anomaly | Explanation |
|---|---|
| Update anomaly | If Ananya moves to another city, multiple rows must be updated. |
| Insertion anomaly | A new customer cannot easily be stored unless an order is also recorded, depending on the table design. |
| Deletion anomaly | Deleting the only order of a customer may accidentally remove the customer's details. |

Normalization addresses these problems by separating data according to its meaning and dependencies.

---

## 3. First Normal Form (1NF)

**Definition:** A table is in First Normal Form when each field contains a single value, and there are no repeating groups of values within a row.

### Example: Violating 1NF

| Order ID | Customer | Products |
|---|---|---|
| 101 | Ananya | Laptop, Mouse |
| 102 | Rahul | Keyboard, Monitor |

The `Products` column contains multiple values in a single cell.

### Convert to 1NF

| Order ID | Customer | Product |
|---|---|---|
| 101 | Ananya | Laptop |
| 101 | Ananya | Mouse |
| 102 | Rahul | Keyboard |
| 102 | Rahul | Monitor |

Now each cell contains one product value.

**Key takeaway:** One field should represent one value at the chosen level of detail.

Note that atomicity depends on the intended data model. For example, an address may be stored as one string or as separate street, city and postal-code fields depending on requirements.

---

## 4. Second Normal Form (2NF)

**Definition:** A table is in Second Normal Form if it is in 1NF and every non-key attribute depends on the *whole* candidate key, not just part of a composite key.

2NF is especially relevant when a table has a composite key.

### Example: Violating 2NF

Consider an order-items table.

| Order ID | Product ID | Product Name | Quantity |
|---|---|---|---:|
| 101 | P1 | Laptop | 1 |
| 101 | P2 | Mouse | 2 |
| 102 | P2 | Mouse | 1 |

Assume the primary key is `(Order ID, Product ID)`.

- `Quantity` depends on both Order ID and Product ID.
- `Product Name` depends only on Product ID.

Therefore, `Product Name` depends on only part of the composite key. This violates 2NF.

### Convert to 2NF

**Order Items**

| Order ID | Product ID | Quantity |
|---|---|---:|
| 101 | P1 | 1 |
| 101 | P2 | 2 |
| 102 | P2 | 1 |

**Products**

| Product ID | Product Name |
|---|---|
| P1 | Laptop |
| P2 | Mouse |

Now product information is stored separately.

**Key takeaway:** Every non-key attribute must depend on the whole candidate key.

If a table has a single-column candidate key and is already in 1NF, it cannot have a partial dependency on that key.

---

## 5. Third Normal Form (3NF)

**Definition:** A table is in Third Normal Form if it is in 2NF and non-key attributes do not depend transitively on a candidate key.

In simpler terms, a non-key attribute should depend on the key, the whole key and nothing but the key.

### Example: Violating 3NF

Consider a customer table.

| Customer ID | Customer Name | Postal Code | City |
|---|---|---|---|
| C1 | Ananya | 560001 | Bengaluru |
| C2 | Rahul | 570001 | Mysuru |
| C3 | Priya | 560001 | Bengaluru |

Assume each postal code determines one city in this simplified example.

The dependencies are:

- Customer ID → Postal Code
- Postal Code → City

Therefore, City depends on Customer ID indirectly through Postal Code. This is a transitive dependency.

### Convert to 3NF

**Customers**

| Customer ID | Customer Name | Postal Code |
|---|---|---|
| C1 | Ananya | 560001 |
| C2 | Rahul | 570001 |
| C3 | Priya | 560001 |

**Postal Codes**

| Postal Code | City |
|---|---|
| 560001 | Bengaluru |
| 570001 | Mysuru |

Now city information is stored in a separate table.

**Key takeaway:** Non-key attributes should depend directly on candidate keys, not on other non-key attributes.

*Note:* Real-world postal codes do not always map uniquely to a single city. The example assumes a simplified business rule to illustrate the dependency.

---

## 6. Quick comparison of normal forms

| Normal form | Main rule | Problem addressed |
|---|---|---|
| 1NF | Each field contains an atomic value | Repeating groups and multi-valued cells |
| 2NF | No partial dependency on a composite candidate key | Attributes depending on only part of a key |
| 3NF | No inappropriate transitive dependency of non-key attributes on a key | Attributes depending on other non-key attributes |

Higher normal forms exist, including BCNF, 4NF and 5NF, but 1NF, 2NF and 3NF are a useful foundation for introductory database design.

## 7. When should we use Normalization?

Normalization is particularly useful for **operational databases (OLTP)**, where applications frequently insert, update and delete records.

Examples include:

- Banking transactions
- E-commerce orders
- Customer relationship management
- Inventory management
- Hospital management systems

For analytical systems, data engineers may also use dimensional models, such as star schemas, which intentionally repeat descriptive information in dimension tables to simplify reporting and improve usability.

Normalization and dimensional modeling solve different problems; neither is universally better.

## 8. Discussion scenario for students

An online retailer has a table containing:

`OrderID, CustomerID, CustomerName, ProductID, ProductName, Quantity`

Ask students:

1. Which attributes depend on `OrderID`?
2. Which attributes depend on `ProductID`?
3. What should the grain of the order-items table be?
4. How would you split the data into Orders, Customers, Products and Order Items?
5. What anomalies could occur if the data remains in one table?

**Suggested design:**

- `Customers(CustomerID, CustomerName)`
- `Orders(OrderID, CustomerID)`
- `Products(ProductID, ProductName)`
- `OrderItems(OrderID, ProductID, Quantity)`

The primary key of `OrderItems` can be `(OrderID, ProductID)` if each product appears only once per order. Otherwise, use an order-line identifier or an appropriate composite key.

The key lesson is that normalization starts with understanding **entities, keys, functional dependencies and the meaning of each row**.
