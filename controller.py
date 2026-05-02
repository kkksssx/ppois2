import sys
from pathlib import Path
from PyQt5.QtWidgets import QApplication, QMessageBox, QFileDialog
from model import DataManager, FamilyRecord
from view import MainWindow, AddDialog, SearchDialog, DeleteDialog, SelectionDialog, Validators
"""
from view.main_window import MainWindow
from view.add_dialog import AddDialog
from view.search_dialog import SearchDialog
from view.delete_dialog import DeleteDialog
from view.selection_dialog import SelectionDialog
from view.validators import Validators
"""
class AppController:
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.window = MainWindow()
        self.data_manager = DataManager()
        self.validators = Validators()
        self._connect_signals()
        self._auto_load_xmls()
        self._refresh_main_table()

    def _auto_load_xmls(self):
        xml_files = list(self.data_manager.data_dir.glob("*.xml"))
        if xml_files:
            total = sum(self.data_manager.load_single_xml(str(f)) for f in xml_files)
            print(f"Автозагрузка: {total} записей из {len(xml_files)} файлов")

    def _connect_signals(self):
        self.window.action_add.triggered.connect(self.add_record)
        self.window.action_search.triggered.connect(self.search_records)
        self.window.action_delete.triggered.connect(self.delete_records)
        self.window.action_load.triggered.connect(self.load_file)
        self.window.action_save.triggered.connect(self.save_file)
        self.window.action_clear.triggered.connect(self.clear_all)
        self.window.action_exit.triggered.connect(self.app.quit)

        self.window.btn_first.clicked.connect(lambda: self._go_to_page(0))
        self.window.btn_prev.clicked.connect(lambda: self._go_to_page(self.window.current_page - 1))
        self.window.btn_next.clicked.connect(lambda: self._go_to_page(self.window.current_page + 1))
        self.window.btn_last.clicked.connect(self._go_to_last_page)
        self.window.spin_page_size.valueChanged.connect(self._on_page_size_changed)

    def _go_to_page(self, page: int):
        total_pages = max(1, (len(self.data_manager.records) + self.window.page_size - 1) // self.window.page_size)
        self.window.current_page = max(0, min(page, total_pages - 1))
        self._refresh_main_table()

    def _go_to_last_page(self):
        total_pages = max(1, (len(self.data_manager.records) + self.window.page_size - 1) // self.window.page_size)
        self._go_to_page(total_pages - 1)

    def _on_page_size_changed(self):
        self.window.page_size = self.window.spin_page_size.value()
        self.window.current_page = 0
        self._refresh_main_table()

    def _refresh_main_table(self):
        self.window.update_display(self.data_manager.records)
        self.window.statusBar().showMessage(f"Загружено записей: {len(self.data_manager.records)}")

    def add_record(self):
        dialog = AddDialog(self.window)
        if dialog.exec_() == AddDialog.Accepted:
            try:
                record = dialog.get_record()
                if record.is_empty():
                    return QMessageBox.warning(self.window, "Ошибка", "Заполните хотя бы одно поле ФИО!")
                self.data_manager.add_record(record)
                self._refresh_main_table()
                QMessageBox.information(self.window, "Успех", "Запись добавлена!")
            except Exception as e:
                QMessageBox.critical(self.window, "Ошибка", f" {e}")

    def search_records(self):
        dialog = SearchDialog(self.window)
        if dialog.exec_() == SearchDialog.Accepted:
            conditions = dialog.get_conditions()
            valid, msg = self.validators.validate_search_conditions(conditions)
            if not valid:
                return QMessageBox.warning(self.window, "Внимание", msg)
            try:
                results = self.data_manager.search(conditions)
                if not results:
                    return QMessageBox.information(self.window, "Поиск", " Записи не найдены.")

                dialog.show_results(results)
                dialog.btn_res_first.clicked.connect(lambda: self._search_page(dialog, 0))
                dialog.btn_res_prev.clicked.connect(lambda: self._search_page(dialog, dialog.current_page - 1))
                dialog.btn_res_next.clicked.connect(lambda: self._search_page(dialog, dialog.current_page + 1))
                dialog.btn_res_last.clicked.connect(lambda: self._search_last_page(dialog))
                dialog.spin_res_size.valueChanged.connect(lambda: self._search_page_size_changed(dialog))
                dialog.exec_()

                if dialog.get_selected_records():
                    QMessageBox.information(self.window, "Выбрано", f"Выбрано: {len(dialog.get_selected_records())}")
            except Exception as e:
                QMessageBox.critical(self.window, "Ошибка", f" {e}")

    def _search_page(self, dialog, page: int):
        total_pages = max(1, (len(dialog.results) + dialog.page_size - 1) // dialog.page_size)
        dialog.current_page = max(0, min(page, total_pages - 1))
        dialog._update_list()

    def _search_last_page(self, dialog):
        total_pages = max(1, (len(dialog.results) + dialog.page_size - 1) // dialog.page_size)
        self._search_page(dialog, total_pages - 1)

    def _search_page_size_changed(self, dialog):
        dialog.page_size = dialog.spin_res_size.value()
        dialog.current_page = 0
        dialog._update_list()

    def delete_records(self):
        dialog = DeleteDialog(self.window)

        if dialog.exec_() == DeleteDialog.Accepted:
            conditions = dialog.get_conditions()
            valid, msg = self.validators.validate_search_conditions(conditions)
            if not valid:
                return QMessageBox.warning(self.window, "Внимание", msg)

            try:
                found = self.data_manager.search(conditions)
                dialog.show_found_records(found)
                if not found: return

                if dialog.exec_() == 2:
                    # 1. Получаем локальные индексы из диалога
                    selected_local_indices = dialog.get_selected_indices()
                    if not selected_local_indices:
                        return QMessageBox.warning(self.window, "Внимание", " Ничего не выбрано")

                    # 2. Маппим локальные индексы в глобальные (в базе данных)
                    # Используем проверку 'is', чтобы найти тот же самый объект в памяти
                    selected_global_indices = []
                    for local_idx in selected_local_indices:
                        selected_rec = found[local_idx]
                        for g_idx, rec in enumerate(self.data_manager.records):
                            if rec is selected_rec:
                                selected_global_indices.append(g_idx)
                                break

                    # 3. Удаляем по глобальным индексам
                    if selected_global_indices:
                        deleted = self.data_manager.delete_by_indices(selected_global_indices)
                        self._refresh_main_table()
                        QMessageBox.information(self.window, "Готово", f" Удалено записей: {deleted}")

            except Exception as e:
                QMessageBox.critical(self.window, "Ошибка", f" Ошибка удаления:\n{e}")

    def load_file(self):
        filepath, _ = QFileDialog.getOpenFileName(self.window, "Загрузить XML", "", "XML (*.xml)")
        if filepath:
            try:
                count = self.data_manager.load_single_xml(filepath)
                self._refresh_main_table()
                QMessageBox.information(self.window, "Загрузка", f" Загружено: {count}")
            except Exception as e:
                QMessageBox.critical(self.window, "Ошибка", f" {e}")

    def save_file(self):
        if not self.data_manager.records:
            return QMessageBox.warning(self.window, "Внимание", " Нет записей!")
        filepath, _ = QFileDialog.getSaveFileName(self.window, "Сохранить XML", "", "XML (*.xml)")
        if filepath:
            try:
                self.data_manager.save_to_xml(filepath)
                QMessageBox.information(self.window, "Сохранение", "Сохранено")
            except Exception as e:
                QMessageBox.critical(self.window, "Ошибка", f" {e}")

    def clear_all(self):
        if not self.data_manager.records:
            return QMessageBox.information(self.window, "Информация", "ℹ Пусто")
        if QMessageBox.question(self.window, "Подтверждение", " Удалить всё?") == QMessageBox.Yes:
            self.data_manager.clear()
            self._refresh_main_table()
            QMessageBox.information(self.window, "Готово", "Очищено")

    def run(self):
        self.window.show()
        sys.exit(self.app.exec_())