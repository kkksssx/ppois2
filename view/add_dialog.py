from PyQt5.QtWidgets import (
    QDialog, QFormLayout, QGroupBox, QLineEdit,
    QSpinBox, QDoubleSpinBox, QPushButton, QHBoxLayout,
    QMessageBox
)
from model import FamilyRecord
from .validators import Validators


class AddDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Добавить новую запись")
        self.setModal(True)
        self.resize(450, 450)
        self.validators = Validators()
        self._create_ui()

    def _create_ui(self):
        layout = QFormLayout(self)

        group_student = QGroupBox("Информация о студенте")
        layout_student = QFormLayout(group_student)
        self.edit_student = QLineEdit()
        self.edit_student.setPlaceholderText("Иванов Иван Иванович")
        layout_student.addRow("ФИО студента:", self.edit_student)
        layout.addRow(group_student)

        group_father = QGroupBox("Информация об отце")
        layout_father = QFormLayout(group_father)
        self.edit_father = QLineEdit()
        self.edit_father.setPlaceholderText("Иванов Петр Сергеевич")
        layout_father.addRow("ФИО отца:", self.edit_father)

        self.spin_father_earnings = QDoubleSpinBox()
        self.spin_father_earnings.setRange(0, 1000000000)
        self.spin_father_earnings.setDecimals(2)
        self.spin_father_earnings.setValue(0)
        layout_father.addRow("Заработок отца:", self.spin_father_earnings)
        layout.addRow(group_father)

        group_mother = QGroupBox("Информация о матери")
        layout_mother = QFormLayout(group_mother)
        self.edit_mother = QLineEdit()
        self.edit_mother.setPlaceholderText("Иванова Мария Петровна")
        layout_mother.addRow("ФИО матери:", self.edit_mother)

        self.spin_mother_earnings = QDoubleSpinBox()
        self.spin_mother_earnings.setRange(0, 1000000000)
        self.spin_mother_earnings.setDecimals(2)
        self.spin_mother_earnings.setValue(0)
        layout_mother.addRow("Заработок матери:", self.spin_mother_earnings)
        layout.addRow(group_mother)

        group_siblings = QGroupBox("Братья и сестры")
        layout_siblings = QFormLayout(group_siblings)

        self.spin_brothers = QSpinBox()
        self.spin_brothers.setRange(0, 100)
        self.spin_brothers.setValue(0)
        layout_siblings.addRow("Число братьев:", self.spin_brothers)

        self.spin_sisters = QSpinBox()
        self.spin_sisters.setRange(0, 100)
        self.spin_sisters.setValue(0)
        layout_siblings.addRow("Число сестер:", self.spin_sisters)
        layout.addRow(group_siblings)

        btn_layout = QHBoxLayout()
        btn_save = QPushButton("Сохранить")
        btn_save.clicked.connect(self._on_save)
        btn_cancel = QPushButton("Отмена")
        btn_cancel.clicked.connect(self.reject)
        btn_layout.addWidget(btn_save)
        btn_layout.addWidget(btn_cancel)
        layout.addRow(btn_layout)

    def _on_save(self):
        valid, msg = self.validators.validate_fio(self.edit_student.text(), "ФИО студента")
        if not valid:
            QMessageBox.critical(self, "Ошибка валидации", msg)
            return

        valid, msg = self.validators.validate_fio(self.edit_father.text(), "ФИО отца")
        if not valid:
            QMessageBox.critical(self, "Ошибка валидации", msg)
            return

        valid, msg = self.validators.validate_fio(self.edit_mother.text(), "ФИО матери")
        if not valid:
            QMessageBox.critical(self, "Ошибка валидации", msg)
            return

        valid, msg = self.validators.validate_earnings(self.spin_father_earnings.value(), "Заработок отца")
        if not valid:
            QMessageBox.critical(self, "Ошибка валидации", msg)
            return

        valid, msg = self.validators.validate_earnings(self.spin_mother_earnings.value(), "Заработок матери")
        if not valid:
            QMessageBox.critical(self, "Ошибка валидации", msg)
            return

        valid, msg = self.validators.validate_count(self.spin_brothers.value(), "Число братьев")
        if not valid:
            QMessageBox.critical(self, "Ошибка валидации", msg)
            return

        valid, msg = self.validators.validate_count(self.spin_sisters.value(), "Число сестер")
        if not valid:
            QMessageBox.critical(self, "Ошибка валидации", msg)
            return

        if not any([self.edit_student.text().strip(),
                    self.edit_father.text().strip(),
                    self.edit_mother.text().strip()]):
            QMessageBox.critical(self, "Ошибка", "Заполните хотя бы одно поле ФИО!")
            return

        self.accept()

    def get_record(self) -> FamilyRecord:
        return FamilyRecord(
            student_fio=self.edit_student.text().strip(),
            father_fio=self.edit_father.text().strip(),
            father_earnings=self.spin_father_earnings.value(),
            mother_fio=self.edit_mother.text().strip(),
            mother_earnings=self.spin_mother_earnings.value(),
            brothers_count=self.spin_brothers.value(),
            sisters_count=self.spin_sisters.value()
        )