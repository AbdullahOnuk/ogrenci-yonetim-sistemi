import sys
import json
from abc import ABC, abstractmethod
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QMessageBox,
    QTableWidget, QTableWidgetItem, QHBoxLayout, QFormLayout, QDialog
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from datetime import datetime

class FileHandler:
    @staticmethod
    def load_from_file(filename):
        try:
            with open(filename, "r") as file:
                return json.load(file)
        except (FileNotFoundError, json.JSONDecodeError):
            return []

    @staticmethod
    def save_to_file(filename, data):
        with open(filename, "w") as file:
            json.dump(data, file, indent=4)

class Person(ABC):
    def __init__(self, name, age):
        self._name = name
        self._age = age

    def get_name(self):
        return self._name

    def get_age(self):
        return self._age

    @abstractmethod
    def get_details(self):
        pass

class Student(Person):
    def __init__(self, student_id, name, age, class_section):
        super().__init__(name, age)
        self.student_id = student_id
        self.class_section = class_section
        self.disciplinary_records = []

    def add_disciplinary_record(self, record):
        self.disciplinary_records.append(record)

    def get_details(self):
        return {
            "id": self.student_id,
            "name": self._name,
            "age": self._age,
            "class": self.class_section,
            "disciplinary_records": self.disciplinary_records
        }

    @staticmethod
    def create_student(student_id=None, name=None, age=None, class_section=None):
        if student_id is None or name is None or age is None or class_section is None:
            raise ValueError("Tüm parametreler zorunludur!")
        return Student(student_id, name, age, class_section)

class LoginWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Giriş Yap")
        self.setGeometry(100, 100, 300, 250)

        self.username_label = QLabel("Kullanıcı Adı:")
        self.username_input = QLineEdit()
        self.password_label = QLabel("Şifre:")
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)

        self.login_button = QPushButton("Giriş Yap")
        self.login_button.clicked.connect(self.check_credentials)

        layout = QVBoxLayout()
        layout.addWidget(self.username_label)
        layout.addWidget(self.username_input)
        layout.addWidget(self.password_label)
        layout.addWidget(self.password_input)
        layout.addWidget(self.login_button)
        self.setLayout(layout)
#admin kontrol
    def check_credentials(self):
        username = self.username_input.text()
        password = self.password_input.text()

        if username == "admin" and password == "12345":
            QMessageBox.information(self, "Başarılı", "Giriş başarılı! Öğrenci yönetim ekranına yönlendiriliyorsunuz.")
            self.open_student_management()
        else:
            QMessageBox.warning(self, "Hata", "Kullanıcı adı veya şifre yanlış!")

    def open_student_management(self):
        self.student_window = StudentManagementWindow()
        self.student_window.show()
        self.close()

class AddStudentDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Öğrenci Ekle")
        self.setGeometry(200, 200, 300, 300)

        self.name_input = QLineEdit()
        self.age_input = QLineEdit()
        self.class_input = QLineEdit()

        self.add_button = QPushButton("Ekle")
        self.add_button.clicked.connect(self.add_student)
        self.cancel_button = QPushButton("İptal")
        self.cancel_button.clicked.connect(self.reject)

        form_layout = QFormLayout()
        form_layout.addRow("Ad Soyad:", self.name_input)
        form_layout.addRow("Yaş:", self.age_input)
        form_layout.addRow("Sınıf-Şube:", self.class_input)

        button_layout = QHBoxLayout()
        button_layout.addWidget(self.add_button)
        button_layout.addWidget(self.cancel_button)

        layout = QVBoxLayout()
        layout.addLayout(form_layout)
        layout.addLayout(button_layout)
        self.setLayout(layout)

    def add_student(self):
        name = self.name_input.text().strip()
        age = self.age_input.text().strip()
        class_section = self.class_input.text().strip()

        if not name.replace(" ", "").isalpha() or not name:
            QMessageBox.warning(self, "Hata", "Ad Soyad sadece harf ve boşluk içermeli ve boş olmamalıdır!")
            return

        if not age.isdigit() or int(age) <= 0:
            QMessageBox.warning(self, "Hata", "Yaş geçerli bir sayı olmalıdır ve boş olmamalıdır!")
            return

        if not class_section:
            QMessageBox.warning(self, "Hata", "Sınıf-Şube boş olmamalıdır!")
            return

        self.student_data = {
            "name": name,
            "age": int(age),
            "class": class_section
        }
        self.accept()

class DisciplinaryDialog(QDialog):
    def __init__(self, student, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"Disiplin İşlemleri - {student['name']}")
        self.setGeometry(200, 200, 500, 400)
        self.student = student

        self.record_input = QLineEdit()
        self.record_input.setPlaceholderText("Yeni disiplin kaydı ekleyin")
        self.record_input.setFont(QFont("Arial", 12))

        self.add_button = QPushButton("Ekle")
        self.add_button.clicked.connect(self.add_record)

        self.remove_button = QPushButton("Seçili Kaydı Sil")
        self.remove_button.clicked.connect(self.remove_record)

        self.records_table = QTableWidget()
        self.records_table.setColumnCount(1)
        self.records_table.setHorizontalHeaderLabels(["Disiplin Kayıtları"])
        self.records_table.setFont(QFont("Arial", 12))
        self.records_table.horizontalHeader().setDefaultSectionSize(400)
        self.records_table.setColumnWidth(0, 500)
        self.load_records()

        layout = QVBoxLayout()
        layout.addWidget(self.record_input)
        layout.addWidget(self.add_button)
        layout.addWidget(self.records_table)
        layout.addWidget(self.remove_button)
        self.setLayout(layout)

    def load_records(self):
        records = self.student.get("disciplinary_records", [])
        self.records_table.setRowCount(len(records))
        for row, record in enumerate(records):
            self.records_table.setItem(row, 0, QTableWidgetItem(record))

    def add_record(self):
        new_record = self.record_input.text()
        if new_record:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            record_with_time = f"{new_record} - {timestamp}"
            self.student.setdefault("disciplinary_records", []).append(record_with_time)
            FileHandler.save_to_file("students.json", self.parent().students)
            self.load_records()
            self.record_input.clear()

            disciplinary_count = len(self.student["disciplinary_records"])
            if disciplinary_count == 3:
                QMessageBox.warning(self, "Uyarı", f"{self.student['name']} okuldan 1 hafta uzaklaştırıldı.")
            elif disciplinary_count == 5:
                QMessageBox.critical(self, "Uyarı", f"{self.student['name']} okuldan atıldı.")
                self.parent().students.remove(self.student)  # Öğrenciyi listeden kaldır

    def remove_record(self):
        selected_row = self.records_table.currentRow()
        if selected_row != -1:
            self.student["disciplinary_records"].pop(selected_row)
            FileHandler.save_to_file("students.json", self.parent().students)
            self.load_records()
        else:
            QMessageBox.warning(self, "Hata", "Silmek için bir kayıt seçin.")

class StudentManagementWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Öğrenci Yönetim Sistemi")
        self.setGeometry(100, 100, 900, 800)

        self.student_table = QTableWidget()
        self.student_table.setColumnCount(5)
        self.student_table.setHorizontalHeaderLabels(["Öğrenci NO", "Ad", "Yaş", "Sınıf", "Ceza Durumu"])
        self.student_table.cellDoubleClicked.connect(self.open_disciplinary_dialog)
        self.student_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.student_table.setFont(QFont("Arial", 12))
        self.student_table.horizontalHeader().setDefaultSectionSize(100)
        self.student_table.setColumnWidth(4, 250)
        self.student_table.setColumnWidth(1, 250)
        self.student_table.setColumnWidth(0, 150)
        self.add_button = QPushButton("Öğrenci Ekle")
        self.add_button.clicked.connect(self.open_add_student_dialog)
        self.remove_button = QPushButton("Seçili Öğrenciyi Sil")
        self.remove_button.clicked.connect(self.remove_student)
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Öğrenci ara...")
        self.search_input.textChanged.connect(self.filter_students)

        self.students = FileHandler.load_from_file("students.json")
        self.sort_students()
        self.load_students()

        button_layout = QHBoxLayout()
        button_layout.addWidget(self.add_button)
        button_layout.addWidget(self.remove_button)

        layout = QVBoxLayout()
        layout.addWidget(self.search_input)
        layout.addWidget(self.student_table)
        layout.addLayout(button_layout)
        self.setLayout(layout)

    def sort_students(self):
        self.students.sort(key=lambda x: (int(x["class"].split("-")[0]), x["class"].split("-")[1]))

    def load_students(self):
        self.student_table.setRowCount(len(self.students))
        for row, student in enumerate(self.students):
            disciplinary_count = len(student.get("disciplinary_records", []))
            status = f"{disciplinary_count} Kayıt - "
            if disciplinary_count >= 5:
                status += "Okuldan Atıldı"
            elif disciplinary_count >= 3:
                status += "Uzaklaştırma"
            else:
                status += "Normal"

            self.student_table.setItem(row, 0, QTableWidgetItem(str(student["id"])))
            self.student_table.setItem(row, 1, QTableWidgetItem(student["name"]))
            self.student_table.setItem(row, 2, QTableWidgetItem(str(student["age"])))
            self.student_table.setItem(row, 3, QTableWidgetItem(student["class"]))
            self.student_table.setItem(row, 4, QTableWidgetItem(status))

    def open_add_student_dialog(self):
        dialog = AddStudentDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            new_student = dialog.student_data
            new_student["id"] = len(self.students) + 1
            new_student["disciplinary_records"] = []
            self.students.append(new_student)
            self.sort_students()
            self.load_students()
            FileHandler.save_to_file("students.json", self.students)

    def remove_student(self):
        selected_row = self.student_table.currentRow()
        if selected_row != -1:
            del self.students[selected_row]
            self.sort_students()
            self.load_students()
            FileHandler.save_to_file("students.json", self.students)
        else:
            QMessageBox.warning(self, "Hata", "Silmek için bir öğrenci seçin.")

    def filter_students(self):
        search_text = self.search_input.text().lower()
        filtered_students = [
            student for student in self.students
            if search_text in student["name"].lower() or search_text in student["class"].lower()
        ]
        self.student_table.setRowCount(len(filtered_students))
        for row, student in enumerate(filtered_students):
            disciplinary_count = len(student.get("disciplinary_records", []))
            status = f"{disciplinary_count} Kayıt - "
            if disciplinary_count >= 5:
                status += "Okuldan Atıldı"
            elif disciplinary_count >= 3:
                status += "Uzaklaştırma"
            else:
                status += "Normal"

            self.student_table.setItem(row, 0, QTableWidgetItem(str(student["id"])))
            self.student_table.setItem(row, 1, QTableWidgetItem(student["name"]))
            self.student_table.setItem(row, 2, QTableWidgetItem(str(student["age"])))
            self.student_table.setItem(row, 3, QTableWidgetItem(student["class"]))
            self.student_table.setItem(row, 4, QTableWidgetItem(status))

    def open_disciplinary_dialog(self, row, column):
        student = self.students[row]
        dialog = DisciplinaryDialog(student, self)
        dialog.exec_()
        self.load_students()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setFont(QFont("Arial", 12)) 
    login_window = LoginWindow()
    login_window.show()
    sys.exit(app.exec_())
