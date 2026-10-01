from pydantic import BaseModel, EmailStr, Field


class Student(BaseModel):
    name: str
    age: int = Field(ge=18)
    email: EmailStr

def register_student(student: Student):
    return f"{student.name} registered successfully"


if __name__ == "__main__":
    # Example usage
    student_data = {
        "name": "Anil Kumar",
        "age": 20,
        "email": "anil.kumar@capstone.com"
    }   

    registered_student = register_student(Student(**student_data))
    print(registered_student)

    student_data_invalid = {
        "name": "Anil Kumar",   
        "age": 17,
        "email": "anil.kumar@capstone.com"
    }

    try:
        register_student(Student(**student_data_invalid))
    except ValueError as e:
        print(f"Error registering student: {e}")    