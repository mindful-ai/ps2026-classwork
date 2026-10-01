# Pydantic — Short Manual

Pydantic is a Python library for **data validation, parsing, and structured data models**. It is especially common in **FastAPI, APIs, configuration management, and AI applications**.

## 1. Installation

```bash
pip install pydantic
```

With `uv`:

```bash
uv add pydantic
```

---

## 2. Basic Model

```python
from pydantic import BaseModel

class Student(BaseModel):
    name: str
    age: int
    email: str
```

Create an object:

```python
student = Student(
    name="Rahul",
    age=21,
    email="rahul@example.com"
)
```

Access values:

```python
print(student.name)
print(student.age)
```

---

## 3. Validation

```python
student = Student(
    name="Rahul",
    age="twenty one",
    email="rahul@example.com"
)
```

Pydantic raises a `ValidationError`.

```python
from pydantic import ValidationError

try:
    student = Student(
        name="Rahul",
        age="twenty one",
        email="rahul@example.com"
    )
except ValidationError as e:
    print(e)
```

---

## 4. Required vs Optional Fields

Required:

```python
class Student(BaseModel):
    name: str
    age: int
```

Optional with a default:

```python
class Student(BaseModel):
    name: str
    age: int
    city: str = "Bangalore"
```

Now this is valid:

```python
student = Student(
    name="Rahul",
    age=21
)
```

---

## 5. Constraints

Use `Field()`:

```python
from pydantic import BaseModel, Field

class Student(BaseModel):
    name: str = Field(min_length=2)
    age: int = Field(ge=18, le=100)
```

Here:

- `min_length=2` → name must have ≥ 2 characters
- `ge=18` → age >= 18
- `le=100` → age <= 100

---

## 6. Special Types

Pydantic provides useful types:

```python
from pydantic import BaseModel, EmailStr, HttpUrl

class User(BaseModel):
    name: str
    email: EmailStr
    website: HttpUrl
```

Now email and URL formats are validated automatically.

---

## 7. Nested Models

```python
from pydantic import BaseModel

class Address(BaseModel):
    city: str
    pincode: int

class Student(BaseModel):
    name: str
    age: int
    address: Address
```

Usage:

```python
student = Student(
    name="Rahul",
    age=21,
    address={
        "city": "Bangalore",
        "pincode": 560001
    }
)
```

---

## 8. Lists

```python
class Student(BaseModel):
    name: str
    skills: list[str]
```

```python
student = Student(
    name="Rahul",
    skills=["Python", "AI", "FastAPI"]
)
```

---

## 9. Dictionaries

```python
class Student(BaseModel):
    name: str
    marks: dict[str, int]
```

```python
student = Student(
    name="Rahul",
    marks={
        "Python": 90,
        "AI": 85
    }
)
```

---

## 10. Convert Model to Dictionary

```python
student.model_dump()
```

Example:

```python
{
    "name": "Rahul",
    "age": 21,
    "email": "rahul@example.com"
}
```

---

## 11. Convert to JSON

```python
student.model_dump_json()
```

---

## 12. Custom Validation

For custom business rules:

```python
from pydantic import BaseModel, field_validator

class Student(BaseModel):
    name: str
    age: int

    @field_validator("name")
    @classmethod
    def validate_name(cls, value):
        if not value.isalpha():
            raise ValueError("Name must contain only letters")
        return value
```

---

# 13. Pydantic's Core Pattern

Remember this pattern:

```python
class ModelName(BaseModel):
    field1: type
    field2: type
    field3: type
```

Then:

```python
obj = ModelName(...)
```

Pydantic performs:

```text
Input
  ↓
Parsing
  ↓
Type validation
  ↓
Constraint validation
  ↓
Custom validation
  ↓
Validated Model
```

---

## 14. Most Important Things to Learn

For a beginner/intermediate Python workshop, focus on these **8 concepts**:

1. `BaseModel`
2. Type annotations
3. Required/default fields
4. `Field()`
5. `ValidationError`
6. Nested models
7. `model_dump()`
8. `field_validator`

Once these are understood, move directly to **Pydantic + FastAPI**, where the value of Pydantic becomes much more apparent.
