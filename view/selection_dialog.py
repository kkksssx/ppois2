from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QListWidget, QListWidgetItem, QPushButton, QMessageBox
)
from typing import List, Optional
from model import FamilyRecord


class SelectionDialog(QDialog):
    def __init__(self, parent=None, records: List[FamilyRecord] = None,
                 title: str = "Выбор записей", multi_select: bool = False):
        super().__init__(parent)
        self.records = records or []
        self.multi_select = multi_select
        self.selected_records: List[FamilyRecord] = []

        self.setWindowTitle(title)
        self.setModal(True)
        self.resize(650, 450)

        self._create_ui()

    def _create_ui(self):
        layout = QVBoxLayout(self)

        if self.multi_select:
            info_text = "Отметьте нужные записи (можно выбрать несколько):"
        else:
            info_text = "Выберите одну запись:"

        info_label = QLabel(info_text)
        info_label.setStyleSheet("font-weight: bold; padding: 5px;")
        layout.addWidget(info_label)

        self.list_widget = QListWidget()
        if self.multi_select:
            self.list_widget.setSelectionMode(QListWidget.MultiSelection)
        else:
            self.list_widget.setSelectionMode(QListWidget.SingleSelection)

        for i, record in enumerate(self.records):
            text = (f"{i + 1}. {record.student_fio}\n"
                    f"   Отец: {record.father_fio} ({record.father_earnings:.2f})\n"
                    f"   Мать: {record.mother_fio} ({record.mother_earnings:.2f})\n"
                    f"   Братьев: {record.brothers_count}, Сестер: {record.sisters_count}")

            item = QListWidgetItem(text)
            self.list_widget.addItem(item)

        layout.addWidget(self.list_widget)

        btn_layout = QHBoxLayout()

        if self.multi_select:
            btn_select_all = QPushButton("✓ Выбрать все")
            btn_select_all.clicked.connect(self._select_all)
            btn_layout.addWidget(btn_select_all)

            btn_deselect_all = QPushButton("✗ Снять выделение")
            btn_deselect_all.clicked.connect(self._deselect_all)
            btn_layout.addWidget(btn_deselect_all)

        btn_select = QPushButton("OK")
        btn_select.clicked.connect(self._on_select)
        btn_layout.addWidget(btn_select)

        btn_cancel = QPushButton("Отмена")
        btn_cancel.clicked.connect(self.reject)
        btn_layout.addWidget(btn_cancel)

        layout.addLayout(btn_layout)

        if self.list_widget.count() > 0:
            self.list_widget.setCurrentRow(0)

    def _select_all(self):
        for i in range(self.list_widget.count()):
            item = self.list_widget.item(i)
            if item:
                item.setSelected(True)

    def _deselect_all(self):
        self.list_widget.clearSelection()

    def _on_select(self):
        selected_rows = []
        for item in self.list_widget.selectedItems():
            row = self.list_widget.row(item)
            selected_rows.append(row)

        if not selected_rows:
            QMessageBox.warning(self, "Внимание",
                                "Выберите хотя бы одну запись!")
            return

        self.selected_records = [self.records[i] for i in selected_rows]
        self.accept()

    def get_selected_records(self) -> List[FamilyRecord]:
        return self.selected_records

    def get_selected_record(self) -> Optional[FamilyRecord]:
        if self.selected_records:
            return self.selected_records[0]
        return None