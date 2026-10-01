def register_student(data):
    if "name" not in data:
        raise ValueError("Name is required")

    if "age" not in data:
        raise ValueError("Age is required")

    if not isinstance(data["age"], int):
        raise ValueError("Age must be an integer")

    if data["age"] < 18:
        raise ValueError("Student must be 18 or older")

    if "email" not in data:
        raise ValueError("Email is required")

    if "@" not in data["email"]:
        raise ValueError("Invalid email")

    name = data["name"]
    age = data["age"]
    email = data["email"]

    return f"{name} registered successfully"

if __name__ == "__main__":
    # Example usage
    student_data = {
        "name": "Anil Kumar",
        "age": 20,
        "email": "anil.kumar@capstone.com"
    }

    print(register_student(student_data))