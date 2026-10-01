from student import Student
from student_manager import StudentManager
from storage import Storage

def main():
    storage = Storage()
    student_manager = StudentManager()

    # Load existing students from storage
    existing_students = storage.load()
    student_manager.load_student(existing_students)

    while True:
        print("\nStudent Management System")
        print("1. Add Student")
        print("2. Delete Student")
        print("3. Update Student")
        print("4. View All Students")
        print("5. Exit")

        choice = input("Enter your choice: ")

        if choice == '1':
            name = input("Enter name: ")
            age = int(input("Enter age: "))
            grade = input("Enter grade: ")
            student_id = input("Enter student ID: ")
            student = Student(name, age, grade, student_id)
            student_manager.add_student(student)
            storage.save(student_manager.to_dict_list())
            print("Student added successfully.")

        elif choice == '2':
            student_id = input("Enter student ID to delete: ")
            try:
                student = student_manager.get_student(student_id)
                student_manager.delete_student(student)
                storage.save(student_manager.to_dict_list())
                print("Student deleted successfully.")
            except KeyError as e:
                print(e)

        elif choice == '3':
            student_id = input("Enter student ID to update: ")
            try:
                student = student_manager.get_student(student_id)
                name = input(f"Enter new name (current: {student.name}): ") or student.name
                age_input = input(f"Enter new age (current: {student.age}): ")
                age = int(age_input) if age_input else student.age
                grade = input(f"Enter new grade (current: {student.grade}): ") or student.grade
                student_manager.update_student(student_id, name=name, age=age, grade=grade)
                storage.save(student_manager.to_dict_list())
                print("Student updated successfully.")
            except KeyError as e:
                print(e)

        elif choice == '4':
            students = student_manager.get_all_students()
            for s in students:
                print(s.get_details())

        elif choice == '5':
            break

        else:
            print("Invalid choice. Please try again.")


if __name__ == "__main__":
    main()