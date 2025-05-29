import sqlite3

class DBLoader:
    def __init__(self):
        self.conn = sqlite3.connect("schedule.db")
        self.cursor = self.conn.cursor()

    def insert_group(self, group_name):
        try:
            self.cursor.execute("INSERT OR IGNORE INTO groups (name) VALUES (?)", (group_name,))
            self.conn.commit()
        except Exception as e:
            print(f"Ошибка при вставке группы: {e}")

    def insert_week(self, week_number, year, start_date=None, end_date=None):
        try:
            self.cursor.execute("""
                INSERT OR IGNORE INTO weeks (week_number, year, start_date, end_date) 
                VALUES (?, ?, ?, ?)
            """, (week_number, year, start_date, end_date))
            self.conn.commit()
        except Exception as e:
            print(f"Ошибка при вставке недели: {e}")

    def insert_teacher(self, full_name):
        try:
            self.cursor.execute("INSERT OR IGNORE INTO teachers (full_name) VALUES (?)", (full_name,))
            self.conn.commit()
        except Exception as e:
            print(f"Ошибка при вставке преподавателя: {e}")

    def insert_room(self, room_name):
        try:
            self.cursor.execute("INSERT OR IGNORE INTO rooms (name) VALUES (?)", (room_name,))
            self.conn.commit()
        except Exception as e:
            print(f"Ошибка при вставке аудитории: {e}")

    def insert_lesson(self, group_id, week_id, day_of_week, lesson_number, subject, teacher_id=None, room_id=None):
        try:
            self.cursor.execute("""
                INSERT INTO lessons (
                    group_id, week_id, day_of_week, lesson_number, subject, teacher_id, room_id
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (group_id, week_id, day_of_week, lesson_number, subject, teacher_id, room_id))
            self.conn.commit()
        except Exception as e:
            print(f"Ошибка при вставке пары: {e}")

    def get_group_id(self, group_name):
        self.cursor.execute("SELECT id FROM groups WHERE name = ?", (group_name,))
        result = self.cursor.fetchone()
        return result[0] if result else None
    def get_teacher_id(self, full_name):
        try:
            self.cursor.execute("SELECT id FROM teachers WHERE full_name = ?", (full_name,))
            result = self.cursor.fetchone()
            return result[0] if result else None
        except Exception as e:
            print(f"Ошибка при получении ID преподавателя: {e}")
            return None

    def get_room_id(self, room_name):
        try:
            self.cursor.execute("SELECT id FROM rooms WHERE name = ?", (room_name,))
            result = self.cursor.fetchone()
            return result[0] if result else None
        except Exception as e:
            print(f"Ошибка при получении ID аудитории: {e}")
            return None
    
    def get_week_id(self, week_number, year):
        try:
            self.cursor.execute("SELECT id FROM weeks WHERE week_number = ? AND year = ?", (week_number, year))
            result = self.cursor.fetchone()
            return result[0] if result else None
        except Exception as e:
            print(f"Ошибка при получении ID недели: {e}")
            return None
        
    def get_group_id(self, group_name):
        self.cursor.execute("SELECT id FROM groups WHERE name = ?", (group_name,))
        result = self.cursor.fetchone()
        return result[0] if result else None
    
    def get_teacher_id(self, full_name):
        self.cursor.execute("SELECT id FROM teachers WHERE full_name = ?", (full_name,))
        result = self.cursor.fetchone()
        return result[0] if result else None
    
    def get_room_id(self, room_name):
        self.cursor.execute("SELECT id FROM rooms WHERE name = ?", (room_name,))
        result = self.cursor.fetchone()
        return result[0] if result else None
    
    def get_week_id(self, week_number, year):
        self.cursor.execute("SELECT id FROM weeks WHERE week_number = ? AND year = ?", (week_number, year))
        result = self.cursor.fetchone()
        return result[0] if result else None
    
    def load_schedule(self, schedule_data):
        for lesson in schedule_data:
            # 1. Группа
            group_name = lesson["group"]
            self.insert_group(group_name)
            self.cursor.execute("SELECT id FROM groups WHERE name = ?", (group_name,))
            group_id = self.cursor.fetchone()[0]

           # Вставка недели и получение week_id
            week_number = lesson["week_number"]
            year = lesson["year"]
            start_date = lesson.get("start_date")
            end_date = lesson.get("end_date")
            
            self.insert_week(week_number, year, start_date, end_date)
            self.cursor.execute("SELECT id FROM weeks WHERE week_number = ? AND year = ?", (week_number, year))
            week_id = self.cursor.fetchone()[0]
            
            # Вставка преподавателя и получение teacher_id
            teacher_name = lesson.get("teacher")
            teacher_id = None
            if teacher_name:
                self.insert_teacher(teacher_name)
                self.cursor.execute("SELECT id FROM teachers WHERE full_name = ?", (teacher_name,))
                teacher_id = self.cursor.fetchone()[0]
            
            # Вставка аудитории и получение room_id
            room_name = lesson.get("room")
            room_id = None
            if room_name:
                self.insert_room(room_name)
                self.cursor.execute("SELECT id FROM rooms WHERE name = ?", (room_name,))
                room_id = self.cursor.fetchone()[0]
            
            # Вставка пары
            self.insert_lesson(
                group_id=group_id,
                week_id=week_id,
                day_of_week=lesson["day_of_week"],
                lesson_number=lesson["lesson_number"],
                subject=lesson["subject"],
                teacher_id=teacher_id,
                room_id=room_id
            )
            pass      
    def get_schedule(self, group_name, week_number, year):
        query = """
        SELECT lessons.day_of_week, lessons.lesson_number, lessons.subject, teachers.full_name, rooms.name
        FROM lessons
        JOIN groups ON lessons.group_id = groups.id
        JOIN weeks ON lessons.week_id = weeks.id
        LEFT JOIN teachers ON lessons.teacher_id = teachers.id
        LEFT JOIN rooms ON lessons.room_id = rooms.id
        WHERE groups.name = ?
          AND weeks.week_number = ?
          AND weeks.year = ?
        ORDER BY lessons.day_of_week, lessons.lesson_number
        """
        self.cursor.execute(query, (group_name, week_number, year))
        return self.cursor.fetchall()
  
        
    def close(self):
        self.conn.close()
