from db_loader import DBLoader

def main():
    loader = DBLoader()

    # Добавим тестовые данные
    loader.insert_group("М3О-203Б")
    loader.insert_week(17, 2025, "2025-04-21", "2025-04-27")
    loader.insert_teacher("Иванов И.И.")
    loader.insert_room("А-101")

    group_id = loader.get_group_id("М3О-203Б")
    week_id = loader.get_week_id(17, 2025)
    teacher_id = loader.get_teacher_id("Иванов И.И.")
    room_id = loader.get_room_id("А-101")

    loader.insert_lesson(
        group_id=group_id,
        week_id=week_id,
        day_of_week="Понедельник",
        lesson_number=1,
        subject="Математика",
        teacher_id=teacher_id,
        room_id=room_id
    )

    # Получим расписание
    schedule = loader.get_schedule("М3О-203Б", 17, 2025)
    print(schedule)

    loader.close()

if __name__ == "__main__":
    main()
