from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTableWidget, QTableWidgetItem, QLabel, QPushButton,
    QSpinBox, QMenuBar, QMenu, QAction, QToolBar, QStatusBar,
    QAbstractItemView
)
from typing import List
from model import FamilyRecord


class MainWindow(QMainWindow):
    """Главное окно приложения"""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Семейные записи студентов (Вариант 10)")
        self.resize(1200, 700)

        self.current_page = 0
        self.page_size = 10
        self.all_records: List[FamilyRecord] = []

        self._create_ui()
        self._create_menu()
        self._create_toolbar()
        self._create_statusbar()

    def _create_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)

        title = QLabel("Список записей о студентах и их семьях")
        title.setStyleSheet("font-size: 18px; font-weight: bold; margin: 10px;")
        layout.addWidget(title)

        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels([
            "ФИО студента", "ФИО отца", "Заработок отца",
            "ФИО матери", "Заработок матери", "Братьев", "Сестер"
        ])
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.table.horizontalHeader().setStretchLastSection(True)

        self.table.setColumnWidth(0, 250)
        self.table.setColumnWidth(1, 220)
        self.table.setColumnWidth(2, 120)
        self.table.setColumnWidth(3, 220)
        self.table.setColumnWidth(4, 120)
        self.table.setColumnWidth(5, 80)
        self.table.setColumnWidth(6, 80)

        layout.addWidget(self.table)

        page_layout = QHBoxLayout()

        self.btn_first = QPushButton("⏮ Первая")
        self.btn_prev = QPushButton("◀ Назад")
        self.lbl_page = QLabel("Страница 1 из 1")
        self.btn_next = QPushButton("Вперед ▶")
        self.btn_last = QPushButton("Последняя ⏭")

        self.spin_page_size = QSpinBox()
        self.spin_page_size.setRange(5, 50)
        self.spin_page_size.setValue(10)
        lbl_size = QLabel("Записей на странице:")

        self.lbl_total = QLabel("Всего записей: 0")

        for w in [self.btn_first, self.btn_prev, self.lbl_page,
                  self.btn_next, self.btn_last, lbl_size,
                  self.spin_page_size, self.lbl_total]:
            page_layout.addWidget(w)

        layout.addLayout(page_layout)

    def _create_menu(self):
        menubar = self.menuBar()

        file_menu = menubar.addMenu("Файл")
        self.action_load = QAction("Загрузить из XML", self)
        self.action_load.setShortcut("Ctrl+O")
        file_menu.addAction(self.action_load)

        self.action_save = QAction("Сохранить в XML", self)
        self.action_save.setShortcut("Ctrl+S")
        file_menu.addAction(self.action_save)

        file_menu.addSeparator()

        self.action_exit = QAction("Выход", self)
        self.action_exit.setShortcut("Ctrl+Q")
        file_menu.addAction(self.action_exit)

        records_menu = menubar.addMenu("Записи")
        self.action_add = QAction("Добавить запись", self)
        self.action_add.setShortcut("Ctrl+N")
        records_menu.addAction(self.action_add)

        self.action_search = QAction("Поиск записей", self)
        self.action_search.setShortcut("Ctrl+F")
        records_menu.addAction(self.action_search)

        self.action_delete = QAction("Удалить по условиям", self)
        self.action_delete.setShortcut("Del")
        records_menu.addAction(self.action_delete)

        records_menu.addSeparator()

        self.action_clear = QAction("Очистить все", self)
        records_menu.addAction(self.action_clear)

    def _create_toolbar(self):
        toolbar = QToolBar("Панель инструментов")
        toolbar.setMovable(False)
        self.addToolBar(toolbar)

        toolbar.addAction(self.action_add)
        toolbar.addAction(self.action_search)
        toolbar.addAction(self.action_delete)
        toolbar.addSeparator()
        toolbar.addAction(self.action_load)
        toolbar.addAction(self.action_save)

    def _create_statusbar(self):
        self.statusBar().showMessage("Готов к работе")

    def update_display(self, records: List[FamilyRecord]):
        self.all_records = records
        total = len(records)
        total_pages = max(1, (total + self.page_size - 1) // self.page_size)

        if self.current_page >= total_pages:
            self.current_page = max(0, total_pages - 1)

        start = self.current_page * self.page_size
        end = min(start + self.page_size, total)
        page_records = records[start:end]

        self.table.setRowCount(len(page_records))

        for row, record in enumerate(page_records):
            self.table.setItem(row, 0, QTableWidgetItem(record.student_fio))
            self.table.setItem(row, 1, QTableWidgetItem(record.father_fio))
            self.table.setItem(row, 2, QTableWidgetItem(f"{record.father_earnings:.2f}"))
            self.table.setItem(row, 3, QTableWidgetItem(record.mother_fio))
            self.table.setItem(row, 4, QTableWidgetItem(f"{record.mother_earnings:.2f}"))
            self.table.setItem(row, 5, QTableWidgetItem(str(record.brothers_count)))
            self.table.setItem(row, 6, QTableWidgetItem(str(record.sisters_count)))

        self.lbl_page.setText(f"Страница {self.current_page + 1} из {total_pages}")
        self.lbl_total.setText(f"Всего записей: {total}")

        self.btn_first.setEnabled(self.current_page > 0)
        self.btn_prev.setEnabled(self.current_page > 0)
        self.btn_next.setEnabled(self.current_page < total_pages - 1)
        self.btn_last.setEnabled(self.current_page < total_pages - 1)