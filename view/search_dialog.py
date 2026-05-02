from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QGroupBox,
    QFormLayout, QLabel, QLineEdit, QDoubleSpinBox,
    QSpinBox, QPushButton, QListWidget, QListWidgetItem,
    QMessageBox
)
from PyQt5.QtCore import Qt
from typing import List, Set
from model import FamilyRecord


class SearchDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Поиск записей")
        self.setModal(True)
        self.resize(950, 750)
        self.results: List[FamilyRecord] = []
        self.current_page = 0
        self.page_size = 10
        self.selected_indices: Set[int] = set()
        self._create_ui()

    def _create_ui(self):
        layout = QVBoxLayout(self)

        group_conditions = QGroupBox("Условия поиска")
        form = QFormLayout(group_conditions)

        self.cond_student = QLineEdit()
        self.cond_student.setPlaceholderText("Часть ФИО (необязательно)")
        form.addRow("ФИО студента:", self.cond_student)

        self.cond_father = QLineEdit()
        self.cond_father.setPlaceholderText("Часть ФИО (необязательно)")
        form.addRow("ФИО отца:", self.cond_father)

        self.cond_mother = QLineEdit()
        self.cond_mother.setPlaceholderText("Часть ФИО (необязательно)")
        form.addRow("ФИО матери:", self.cond_mother)

        earn_father_layout = QHBoxLayout()
        self.cond_father_min = QDoubleSpinBox()
        self.cond_father_min.setRange(0, 1000000000)
        self.cond_father_min.setDecimals(2)
        self.cond_father_min.setValue(0)
        earn_father_layout.addWidget(self.cond_father_min)
        earn_father_layout.addWidget(QLabel("до"))
        self.cond_father_max = QDoubleSpinBox()
        self.cond_father_max.setRange(0, 1000000000)
        self.cond_father_max.setDecimals(2)
        self.cond_father_max.setValue(0)
        earn_father_layout.addWidget(self.cond_father_max)
        form.addRow("Заработок отца:", earn_father_layout)

        earn_mother_layout = QHBoxLayout()
        self.cond_mother_min = QDoubleSpinBox()
        self.cond_mother_min.setRange(0, 1000000000)
        self.cond_mother_min.setDecimals(2)
        self.cond_mother_min.setValue(0)
        earn_mother_layout.addWidget(self.cond_mother_min)
        earn_mother_layout.addWidget(QLabel("до"))
        self.cond_mother_max = QDoubleSpinBox()
        self.cond_mother_max.setRange(0, 1000000000)
        self.cond_mother_max.setDecimals(2)
        self.cond_mother_max.setValue(0)
        earn_mother_layout.addWidget(self.cond_mother_max)
        form.addRow("Заработок матери:", earn_mother_layout)

        self.cond_brothers = QSpinBox()
        self.cond_brothers.setRange(0, 100)
        self.cond_brothers.setValue(0)
        form.addRow("Число братьев:", self.cond_brothers)

        self.cond_sisters = QSpinBox()
        self.cond_sisters.setRange(0, 100)
        self.cond_sisters.setValue(0)
        form.addRow("Число сестер:", self.cond_sisters)

        layout.addWidget(group_conditions)

        btn_search = QPushButton("Найти")
        btn_search.setStyleSheet("background-color: #4CAF50; color: white; padding: 8px; font-weight: bold;")
        btn_search.clicked.connect(self.accept)
        layout.addWidget(btn_search)

        group_results = QGroupBox("Результаты поиска (отметьте нужные)")
        layout_results = QVBoxLayout(group_results)

        self.list_widget = QListWidget()
        self.list_widget.setSelectionMode(QListWidget.MultiSelection)
        layout_results.addWidget(self.list_widget)

        page_layout = QHBoxLayout()
        self.btn_res_first = QPushButton("⏮")
        self.btn_res_prev = QPushButton("◀")
        self.lbl_res_page = QLabel("Стр. 1 из 1")
        self.btn_res_next = QPushButton("▶")
        self.btn_res_last = QPushButton("⏭")
        self.spin_res_size = QSpinBox()
        self.spin_res_size.setRange(5, 50)
        self.spin_res_size.setValue(10)
        self.lbl_res_total = QLabel("Всего: 0")

        for w in [self.btn_res_first, self.btn_res_prev, self.lbl_res_page,
                  self.btn_res_next, self.btn_res_last,
                  QLabel("На стр:"), self.spin_res_size, self.lbl_res_total]:
            page_layout.addWidget(w)

        layout_results.addLayout(page_layout)
        layout.addWidget(group_results)

        btn_actions = QHBoxLayout()
        btn_select_all = QPushButton(" Выбрать все")
        btn_select_all.clicked.connect(self._select_all)
        btn_deselect_all = QPushButton(" Снять выделение")
        btn_deselect_all.clicked.connect(self._deselect_all)
        btn_ok = QPushButton("OK")
        btn_ok.clicked.connect(self._on_ok)
        btn_close = QPushButton("Закрыть")
        btn_close.clicked.connect(self.reject)

        for btn in [btn_select_all, btn_deselect_all, btn_ok, btn_close]:
            btn_actions.addWidget(btn)

        layout.addLayout(btn_actions)

    def _select_all(self):
        for i in range(self.list_widget.count()):
            item = self.list_widget.item(i)
            if item:
                item.setSelected(True)

    def _deselect_all(self):
        self.list_widget.clearSelection()

    def _on_ok(self):
        selected = [i for i in range(self.list_widget.count())
                    if self.list_widget.item(i).isSelected()]

        if not selected:
            reply = QMessageBox.question(
                self, "Подтверждение",
                "Ни одна запись не выбрана. Закрыть диалог?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            if reply != QMessageBox.Yes:
                return

        self.accept()

    def get_conditions(self) -> dict:
        conditions = {}

        if self.cond_student.text().strip():
            conditions['student_fio'] = self.cond_student.text().strip()
        if self.cond_father.text().strip():
            conditions['father_fio'] = self.cond_father.text().strip()
        if self.cond_mother.text().strip():
            conditions['mother_fio'] = self.cond_mother.text().strip()

        f_min = self.cond_father_min.value()
        f_max = self.cond_father_max.value()
        if f_min > 0 or f_max > 0:
            conditions['father_earnings'] = (
                f_min if f_min > 0 else None,
                f_max if f_max > 0 else None
            )

        m_min = self.cond_mother_min.value()
        m_max = self.cond_mother_max.value()
        if m_min > 0 or m_max > 0:
            conditions['mother_earnings'] = (
                m_min if m_min > 0 else None,
                m_max if m_max > 0 else None
            )

        if self.cond_brothers.value() > 0:
            conditions['brothers_count'] = self.cond_brothers.value()
        if self.cond_sisters.value() > 0:
            conditions['sisters_count'] = self.cond_sisters.value()

        return conditions

    def show_results(self, records: List[FamilyRecord]):
        self.results = records
        self.current_page = 0
        self._update_list()

    def _update_list(self):
        total = len(self.results)
        total_pages = max(1, (total + self.page_size - 1) // self.page_size)

        if self.current_page >= total_pages:
            self.current_page = max(0, total_pages - 1)

        start = self.current_page * self.page_size
        end = min(start + self.page_size, total)
        page_records = self.results[start:end]

        self.list_widget.clear()

        for i, record in enumerate(page_records):
            global_idx = start + i
            text = (f"{record.student_fio}\n"
                    f"  Отец: {record.father_fio} ({record.father_earnings:.2f})\n"
                    f"  Мать: {record.mother_fio} ({record.mother_earnings:.2f})\n"
                    f"  Братьев: {record.brothers_count}, Сестер: {record.sisters_count}")

            item = QListWidgetItem(text)
            item.setData(Qt.UserRole, global_idx)

            if global_idx in self.selected_indices:
                item.setSelected(True)

            self.list_widget.addItem(item)

        self.lbl_res_page.setText(f"Стр. {self.current_page + 1} из {total_pages}")
        self.lbl_res_total.setText(f"Всего: {total}")

        self.btn_res_first.setEnabled(self.current_page > 0)
        self.btn_res_prev.setEnabled(self.current_page > 0)
        self.btn_res_next.setEnabled(self.current_page < total_pages - 1)
        self.btn_res_last.setEnabled(self.current_page < total_pages - 1)

    def get_selected_records(self) -> List[FamilyRecord]:
        selected = []
        for i in range(self.list_widget.count()):
            item = self.list_widget.item(i)
            if item and item.isSelected():
                idx = item.data(Qt.UserRole)
                if 0 <= idx < len(self.results):
                    selected.append(self.results[idx])
        return selected