import sqlite3

def get_schedule_for_group(group_name):
    conn = sqlite3.connect("schedule.db")
    cursor = conn.cursor()

    query = """
    SELECT 
        w.week_number,
        l.day_of_week,
        l.lesson_number,
        l.subject,
        t.full_name AS teacher_name,
        r.name AS room_name
    FROM lessons l
    JOIN groups g ON l.group_id = g.id
    JOIN weeks w ON l.week_id = w.id
    LEFT JOIN teachers t ON l.teacher_id = t.id
    LEFT JOIN rooms r ON l.room_id = r.id
    WHERE g.name = ?
    ORDER BY w.week_number, l.day_of_week, l.lesson_number
    """

    cursor.execute(query, (group_name,))
    rows = cursor.fetchall()

    if not rows:
        print(f"Для группы {group_name} расписание не найдено.")
        return

    print(f"📅 Расписание для группы {group_name}:\n")

    for row in rows:
        week, day, num, subject, teacher, room = row
        print(f"Неделя {week} — {day}, {num}-я пара:")
        print(f"  📘 Предмет: {subject}")
        print(f"  👨‍🏫 Преподаватель: {teacher if teacher else 'Не указан'}")
        print(f"  🏫 Аудитория: {room if room else 'Не указана'}\n")

    conn.close()

# Запуск
if __name__ == "__main__":
    get_schedule_for_group("ИУ7-101")
