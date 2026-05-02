from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QGroupBox,
    QFormLayout, QLabel, QLineEdit, QDoubleSpinBox,
    QSpinBox, QPushButton, QListWidget, QListWidgetItem,
    QMessageBox
)
from typing import List, Set
from model import FamilyRecord


class DeleteDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Удаление записей")
        self.setModal(True)
        self.resize(700, 600)
        self.found_records: List[FamilyRecord] = []
        self._create_ui()

    def _create_ui(self):
        layout = QVBoxLayout(self)

        warning = QLabel("Заполните условия для поиска записей на удаление")
        warning.setStyleSheet("color: red; font-weight: bold; padding: 10px;")
        layout.addWidget(warning)

        group = QGroupBox("Условия поиска")
        form = QFormLayout(group)

        self.cond_student = QLineEdit()
        form.addRow("ФИО студента:", self.cond_student)

        self.cond_father = QLineEdit()
        form.addRow("ФИО отца:", self.cond_father)

        self.cond_mother = QLineEdit()
        form.addRow("ФИО матери:", self.cond_mother)

        earn_f_layout = QHBoxLayout()
        self.cond_father_min = QDoubleSpinBox()
        self.cond_father_min.setRange(0, 1000000000)
        self.cond_father_min.setDecimals(2)
        earn_f_layout.addWidget(self.cond_father_min)
        earn_f_layout.addWidget(QLabel("до"))
        self.cond_father_max = QDoubleSpinBox()
        self.cond_father_max.setRange(0, 1000000000)
        self.cond_father_max.setDecimals(2)
        earn_f_layout.addWidget(self.cond_father_max)
        form.addRow("Заработок отца:", earn_f_layout)

        earn_m_layout = QHBoxLayout()
        self.cond_mother_min = QDoubleSpinBox()
        self.cond_mother_min.setRange(0, 1000000000)
        self.cond_mother_min.setDecimals(2)
        earn_m_layout.addWidget(self.cond_mother_min)
        earn_m_layout.addWidget(QLabel("до"))
        self.cond_mother_max = QDoubleSpinBox()
        self.cond_mother_max.setRange(0, 1000000000)
        self.cond_mother_max.setDecimals(2)
        earn_m_layout.addWidget(self.cond_mother_max)
        form.addRow("Заработок матери:", earn_m_layout)

        self.cond_brothers = QSpinBox()
        self.cond_brothers.setRange(0, 100)
        form.addRow("Число братьев:", self.cond_brothers)

        self.cond_sisters = QSpinBox()
        self.cond_sisters.setRange(0, 100)
        form.addRow("Число сестер:", self.cond_sisters)

        layout.addWidget(group)

        btn_search = QPushButton("Найти записи для удаления")
        btn_search.setStyleSheet("background-color: #2196F3; color: white; padding: 8px; font-weight: bold;")
        btn_search.clicked.connect(self._on_search)
        layout.addWidget(btn_search)

        group_found = QGroupBox("Найденные записи (отметьте для удаления)")
        layout_found = QVBoxLayout(group_found)

        self.list_widget = QListWidget()
        self.list_widget.setSelectionMode(QListWidget.MultiSelection)
        layout_found.addWidget(self.list_widget)
        layout.addWidget(group_found)

        btn_actions = QHBoxLayout()
        btn_select_all = QPushButton("✓ Все")
        btn_select_all.clicked.connect(self._select_all)
        btn_deselect_all = QPushButton("✗ Снять")
        btn_deselect_all.clicked.connect(self._deselect_all)
        btn_delete = QPushButton(" Удалить выбранные")
        btn_delete.setStyleSheet("background-color: #f44336; color: white; padding: 8px; font-weight: bold;")
        btn_delete.clicked.connect(self._on_delete)
        btn_cancel = QPushButton(" Отмена")
        btn_cancel.clicked.connect(self.reject)

        for btn in [btn_select_all, btn_deselect_all, btn_delete, btn_cancel]:
            btn_actions.addWidget(btn)

        layout.addLayout(btn_actions)

    def _on_search(self):
        if self._no_conditions():
            QMessageBox.warning(self, "Внимание", "Заполните хотя бы одно условие!")
            return
        self.accept()

    def _select_all(self):
        for i in range(self.list_widget.count()):
            item = self.list_widget.item(i)
            if item: item.setSelected(True)

    def _deselect_all(self):
        self.list_widget.clearSelection()

    def _on_delete(self):
        if not self.get_selected_indices():
            QMessageBox.warning(self, "Внимание", "Выберите хотя бы одну запись!")
            return

        count = len(self.get_selected_indices())
        reply = QMessageBox.question(
            self, "Подтверждение",
            f"Удалить {count} записей? Это действие нельзя отменить!",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            self.done(2)

    def _no_conditions(self) -> bool:
        return (
                not self.cond_student.text().strip() and
                not self.cond_father.text().strip() and
                not self.cond_mother.text().strip() and
                self.cond_father_min.value() == 0 and self.cond_father_max.value() == 0 and
                self.cond_mother_min.value() == 0 and self.cond_mother_max.value() == 0 and
                self.cond_brothers.value() == 0 and self.cond_sisters.value() == 0
        )

    def get_conditions(self) -> dict:
        conditions = {}
        if self.cond_student.text().strip(): conditions['student_fio'] = self.cond_student.text().strip()
        if self.cond_father.text().strip(): conditions['father_fio'] = self.cond_father.text().strip()
        if self.cond_mother.text().strip(): conditions['mother_fio'] = self.cond_mother.text().strip()

        f_min, f_max = self.cond_father_min.value(), self.cond_father_max.value()
        if f_min > 0 or f_max > 0: conditions['father_earnings'] = (f_min if f_min > 0 else None,
                                                                    f_max if f_max > 0 else None)

        m_min, m_max = self.cond_mother_min.value(), self.cond_mother_max.value()
        if m_min > 0 or m_max > 0: conditions['mother_earnings'] = (m_min if m_min > 0 else None,
                                                                    m_max if m_max > 0 else None)

        if self.cond_brothers.value() > 0: conditions['brothers_count'] = self.cond_brothers.value()
        if self.cond_sisters.value() > 0: conditions['sisters_count'] = self.cond_sisters.value()
        return conditions

    def show_found_records(self, records: List[FamilyRecord]):
        self.found_records = records
        self.list_widget.clear()
        for i, record in enumerate(records):
            text = (f"{i + 1}. {record.student_fio}\n"
                    f"   Отец: {record.father_fio} ({record.father_earnings:.2f})\n"
                    f"   Мать: {record.mother_fio} ({record.mother_earnings:.2f})\n"
                    f"   Братьев: {record.brothers_count}, Сестер: {record.sisters_count}")
            self.list_widget.addItem(QListWidgetItem(text))

        if not records:
            QMessageBox.information(self, "Поиск", "Записи не найдены.")

    def get_selected_indices(self) -> List[int]:
        """Возвращает индексы выбранных элементов в списке диалога"""
        return [i for i in range(self.list_widget.count())
                if self.list_widget.item(i).isSelected()]