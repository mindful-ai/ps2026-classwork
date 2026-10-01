from student import Student

class StudentManager:
    def __init__(self):
        self.students = []

    def add_student(self, student):
        if isinstance(student, Student):
            self.students.append(student)
        else:
            raise ValueError("Only Student instances can be added.")

    def delete_student(self, student):
        if student in self.students:
            self.students.remove(student)
        else:
            raise KeyError(f"Student not found: {student}")

    def get_student(self, student_id):
        for student in self.students:
            if student.student_id == student_id:
                return student
        raise KeyError(f"No student found with ID: {student_id}")

    def get_all_students(self):
        return self.students

    def update_student(self, student_id, **kwargs):
        student = self.get_student(student_id)
        for key, value in kwargs.items():
            if hasattr(student, key):
                setattr(student, key, value)
            else:
                raise AttributeError(f"Student has no attribute '{key}'")
            
    def find_by_id(self, student_id):
        return self.get_student(student_id)

    def load_student(self, student_dicts):
        for student_dict in student_dicts:
            student = Student.from_dict(student_dict)
            self.add_student(student)

    def to_dict_list(self):
        return [student.to_dict() for student in self.students]

    