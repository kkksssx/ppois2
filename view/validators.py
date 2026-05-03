import re


class Validators:
    """Валидаторы для полей ввода"""

    @staticmethod
    def validate_fio(text: str, field_name: str = "ФИО"):
        """Проверка ФИО"""
        if not text.strip():
            return True, ""

        text = text.strip()

        if len(text) < 2:
            return False, f"{field_name} должно содержать минимум 2 символа"

        if len(text) > 100:
            return False, f"{field_name} должно содержать максимум 100 символов"

        if not re.match(r'^[а-яА-ЯёЁa-zA-Z\s\-]+$', text):
            return False, f"{field_name} должно содержать только буквы, пробелы и дефис"

        return True, ""

    @staticmethod
    def validate_earnings(value: float, field_name: str = "Заработок"):
        """Проверка заработка"""
        if value < 0:
            return False, f"{field_name} не может быть отрицательным"

        if value > 1_000_000_000:
            return False, f"{field_name} слишком большой (максимум 1 млрд)"

        return True, ""

    @staticmethod
    def validate_count(value: int, field_name: str = "Количество"):
        """Проверка количества"""
        if value < 0:
            return False, f"{field_name} не может быть отрицательным"

        if value > 100:
            return False, f"{field_name} не может быть больше 100"

        return True, ""

    @staticmethod
    def validate_search_conditions(conditions: dict):
        """Проверка условий поиска"""
        filled = 0
        for value in conditions.values():
            if value and (isinstance(value, str) and value.strip() or
                          isinstance(value, (int, float)) and value != 0 or
                          isinstance(value, tuple) and any(v is not None and v != 0 for v in value)):
                filled += 1

        if filled == 0:
            return False, "Заполните хотя бы одно условие"

        return True, ""