class Student:
    def __init__(self, name, age, grade, student_id=None):
        self.name = name
        self.age = age
        self.grade = grade
        self.student_id = student_id

    def get_details(self):
        if self.student_id is not None:
            return f"Name: {self.name}, Age: {self.age}, Grade: {self.grade}, Student ID: {self.student_id}"
        return f"Name: {self.name}, Age: {self.age}, Grade: {self.grade}"

    def to_dict(self):
        return {
            "name": self.name,
            "age": self.age,
            "grade": self.grade,
            "student_id": self.student_id
        }

    @staticmethod
    def from_dict(data):
        return Student(
            name=data.get("name"),
            age=data.get("age"),
            grade=data.get("grade"),
            student_id=data.get("student_id")
        )