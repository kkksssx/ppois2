import sys
import shutil
from pathlib import Path
from model import DataManager, FamilyRecord


def generate_test_data(filename: str, count: int = 55):
    dm = DataManager()
    dm.records = []  # Гарантируем чистый старт

    first_names = ["Иван", "Петр", "Алексей", "Дмитрий", "Сергей", "Михаил", "Андрей", "Николай", "Владимир", "Павел"]
    last_names = ["Иванов", "Петров", "Сидоров", "Козлов", "Новиков", "Морозов", "Волков", "Лебедев", "Соколов",
                  "Попов"]
    mothers_names = ["Мария", "Анна", "Елена", "Ольга", "Татьяна", "Наталья", "Ирина", "Светлана", "Юлия", "Екатерина"]
    patronymics_m = ["Иванович", "Петрович", "Алексеевич", "Дмитриевич", "Сергеевич", "Михайлович"]
    patronymics_f = ["Ивановна", "Петровна", "Алексеевна", "Дмитриевна", "Сергеевна", "Михайловна"]

    for i in range(count):
        idx = i % len(last_names)
        student = f"{last_names[idx]} {first_names[idx]} {patronymics_m[(i + 2) % len(patronymics_m)]}"
        father = f"{last_names[idx]} {first_names[(i + 1) % len(first_names)]} {patronymics_m[(i + 3) % len(patronymics_m)]}"
        mother = f"{last_names[idx]}а {mothers_names[idx]} {patronymics_f[(i + 4) % len(patronymics_f)]}"

        dm.records.append(FamilyRecord(
            student_fio=student, father_fio=father, mother_fio=mother,
            father_earnings=4500.0 + i * 125.5, mother_earnings=3800.0 + i * 98.75,
            brothers_count=i % 4, sisters_count=i % 3
        ))

    data_dir = Path("data")
    data_dir.mkdir(exist_ok=True)
    dm.save_to_xml(str(data_dir / filename))
    print(f"Создан: {data_dir / filename} ({len(dm.records)} записей)")


if __name__ == "__main__":
    # Удаляем старую папку data, чтобы избежать дублей
    data_dir = Path("data")
    if data_dir.exists():
        shutil.rmtree(data_dir)
        print("Очищена старая папка data/")

    print("Генерация данных...")
    generate_test_data("file1.xml", 55)
    generate_test_data("file2.xml", 60)
    print("\nГотово! Запустите: python main.py")