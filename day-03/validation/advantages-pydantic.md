| Advantage                | Without Pydantic | With Pydantic     |
| ------------------------ | ---------------- | ----------------- |
| Type validation          | Manual           | Automatic         |
| Required fields          | Manual           | Automatic         |
| Constraints              | Manual           | Declarative       |
| Email/URL validation     | Manual           | Built-in types    |
| Data conversion          | Manual           | Automatic parsing |
| Error reporting          | Manual           | Structured        |
| Nested data              | Difficult        | Easy              |
| API request validation   | Lots of code     | Very little code  |
| Documentation            | Manual           | Can be generated  |
| Reusable schemas         | Difficult        | Natural           |
| Maintainability          | Lower            | Higher            |
| Integration with FastAPI | Manual           | Excellent         |

Instead of writing code that describes how to validate data, we describe what valid data looks like.