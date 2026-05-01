import json
import os
import xml.dom.minidom as dom #minidom Это упр реализация Doc obj model Позволяет создавать XML-документы программно
import xml.sax as sax #SAX-парсер для XML читает XML потоком, не загружая весь документ в память
from pathlib import Path
from dataclasses import dataclass, asdict
from typing import List


@dataclass
class FamilyRecord:
    student_fio: str = ""
    father_fio: str = ""
    father_earnings: float = 0.0
    mother_fio: str = ""
    mother_earnings: float = 0.0
    brothers_count: int = 0
    sisters_count: int = 0

    def is_empty(self) -> bool:
        return not (self.student_fio.strip() or self.father_fio.strip() or self.mother_fio.strip())

    def to_dict(self) -> dict:
        return asdict(self) #рекурс преобр записи в словарь

    @classmethod
    def from_dict(cls, data: dict) -> 'FamilyRecord':  # ← переименуйте 'dict' в 'data'
        return cls(
            student_fio=str(data.get('student_fio', '')),
            father_fio=str(data.get('father_fio', '')),
            father_earnings=float(data.get('father_earnings', 0)),
            mother_fio=str(data.get('mother_fio', '')),
            mother_earnings=float(data.get('mother_earnings', 0)),
            brothers_count=int(data.get('brothers_count', 0)),
            sisters_count=int(data.get('sisters_count', 0))
        )


class SAXHandler(sax.ContentHandler):    #насл. от базового класса для обработки XML-событий
    def __init__(self):
        super().__init__()
        self.records = []
        self.current_record = {}
        self.current_tag = ""
        self.current_data = ""

    def startElement(self, name, attributes):
        self.current_tag = name
        self.current_data = ""
        if name == "record":
            self.current_record = {}

    def endElement(self, name):
        if name == "record":
            if self.current_record:
                record = FamilyRecord.from_dict(self.current_record)
                if not record.is_empty():
                    self.records.append(record)
        elif name in ['student_fio', 'father_fio', 'mother_fio',
                      'father_earnings', 'mother_earnings',
                      'brothers_count', 'sisters_count']:
            self.current_record[name] = self.current_data.strip()
        self.current_tag = ""

    def characters(self, content):
        self.current_data += content


class DataManager:
    def __init__(self):
        self.records: List[FamilyRecord] = []
        self.data_dir = Path("data")
        self.data_dir.mkdir(exist_ok=True)
        self.auto_file = self.data_dir / "autosave.json"


    def add_record(self, record: FamilyRecord):
        if record.is_empty():
            raise ValueError("Запись не может быть пустой")
        self.records.append(record)
        self._save_auto()

    def delete_by_indices(self, indices: List[int]) -> int:
        if not indices:
            return 0
        deleted = 0
        for i in sorted(indices, reverse=True):
            if 0 <= i < len(self.records):
                del self.records[i]
                deleted += 1
        if deleted > 0:
            self._save_auto()
        return deleted

    def delete_by_conditions(self, conditions: dict) -> int:
        indices = [i for i, r in enumerate(self.records) if self._matches(r, conditions)]
        return self.delete_by_indices(indices)

    def search(self, conditions: dict) -> List[FamilyRecord]:
        return [r for r in self.records if self._matches(r, conditions)]

    def _matches(self, record: FamilyRecord, conditions: dict) -> bool:
        """Проверка соответствия записи условиям"""
        for field, value in conditions.items():
            if value is None or value == "" or value == 0:
                continue

            record_value = getattr(record, field, None)

            if field.endswith('_fio'):
                record_words = str(record_value).split()
                search_words = value.split()

                #есть ли хотя бы одно слово из поиска в ФИО
                found = False
                for search_word in search_words:
                    for record_word in record_words:
                        if search_word.lower() == record_word.lower():
                            found = True
                            break
                    if found:
                        break

                if not found:
                    return False

            elif field.endswith('_earnings'):
                if isinstance(value, tuple):
                    min_val, max_val = value
                    if min_val is not None and record_value < min_val:
                        return False
                    if max_val is not None and record_value > max_val:
                        return False
                else:
                    if abs(record_value - float(value)) > 0.01:
                        return False
            else:
                if record_value != int(value):
                    return False

        return True

    def save_to_xml(self, filepath: str):
        doc = dom.Document()
        root = doc.createElement("records")
        doc.appendChild(root)
        for record in self.records:
            record_elem = doc.createElement("record")
            root.appendChild(record_elem)
            for field_name, value in record.to_dict().items():
                field_elem = doc.createElement(field_name)
                field_elem.appendChild(doc.createTextNode(str(value)))
                record_elem.appendChild(field_elem)
        with open(filepath, 'w', encoding='utf-8') as f:
            doc.writexml(f, indent="  ", addindent="  ", newl="\n", encoding="UTF-8")

    def load_single_xml(self, filepath: str) -> int:
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"Файл не найден: {filepath}")
        parser = sax.make_parser()
        handler = SAXHandler()
        parser.setContentHandler(handler)
        parser.parse(filepath)
        if not handler.records:
            raise ValueError("В файле нет записей")
        self.records.extend(handler.records)
        self._save_auto()
        return len(handler.records)

    def clear(self):
        self.records.clear()
        self._save_auto()

    def _save_auto(self):
        try:
            data = [r.to_dict() for r in self.records]
            with open(self.auto_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Warning: автосохранение не удалось: {e}")