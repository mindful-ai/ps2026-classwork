import unittest 
from student import Student
from student_manager import StudentManager

class TestStudentManager(unittest.TestCase):
    def setUp(self):
        self.manager = StudentManager()
        self.student1 = Student('Alice', 20, 'A', 'S001')
        self.student2 = Student('Bob', 22, 'B', 'S002')

    def test_add_student(self):
        self.manager.add_student(self.student1)
        self.assertEqual(len(self.manager.students), 1)
        self.assertEqual(self.manager.students[0].name, 'Alice')

    def test_delete_student(self):
        self.manager.add_student(self.student1)
        self.manager.delete_student(self.student1)
        self.assertEqual(len(self.manager.students), 0)

    def test_update_student(self):
        self.manager.add_student(self.student1)
        updated_info = {'name': 'Alice Smith', 'age': 21}
        self.manager.update_student('S001', **updated_info)
        student = self.manager.get_student('S001')
        self.assertEqual(student['name'], 'Alice Smith')
        self.assertEqual(student['age'], 21)

    def test_get_student(self):
        self.manager.add_student(self.student1)
        student = self.manager.get_student('S001')
        self.assertEqual(student['name'], 'Alice')

    def test_get_all_students(self):
        self.manager.add_student(self.student1)
        self.manager.add_student(self.student2)
        all_students = self.manager.get_all_students()
        self.assertEqual(len(all_students), 2)

    def tearDown(self):
        return super().tearDown()

if __name__ == '__main__':
    unittest.main()