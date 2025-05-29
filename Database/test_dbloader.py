from db_loader import DBLoader

def main():
    loader = DBLoader()

    # Добавим группы
    groups = ["М3О-203Б", "М3О-204Б", "ИУ7-101"]
    for group in groups:
        loader.insert_group(group)

    # Добавим преподавателей
    teachers = ["Иванов Иван Иванович", "Петров Петр Петрович"]
    for teacher in teachers:
        loader.insert_teacher(teacher)

    # Добавим аудитории
    rooms = ["Аудитория 101", "Аудитория 202"]
    for room in rooms:
        loader.insert_room(room)

    # Добавим недели
    loader.insert_week(20, 2025, "2025-05-12", "2025-05-18")
    loader.insert_week(21, 2025, "2025-05-19", "2025-05-25")

    # Добавим пары
    loader.insert_lesson(
        group_id=1,
        week_id=1,
        day_of_week="Понедельник",
        lesson_number=1,
        subject="Математика",
        teacher_id=1,
        room_id=1
    )

    loader.insert_lesson(
        group_id=2,
        week_id=1,
        day_of_week="Вторник",
        lesson_number=2,
        subject="Физика",
        teacher_id=2,
        room_id=2
    )

    loader.insert_lesson(
        group_id=3,
        week_id=2,
        day_of_week="Среда",
        lesson_number=3,
        subject="Информатика",
        teacher_id=1,
        room_id=1
    )

    loader.close()

if __name__ == "__main__":
    main()
