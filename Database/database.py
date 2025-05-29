import sqlite3

conn = sqlite3.connect("schedule.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS groups (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE
)              
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS weeks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    week_number INTEGER NOT NULL,
    year INTEGER NOT NULL,
    start_date TEXT,
    end_date TEXT,
    UNIQUE(week_number, year)
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS teachers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    full_name TEXT NOT NULL UNIQUE
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS rooms (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS lessons (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    group_id INTEGER NOT NULL,
    week_id INTEGER NOT NULL,
    day_of_week TEXT NOT NULL,
    lesson_number INTEGER NOT NULL,
    subject TEXT NOT NULL,
    teacher_id INTEGER,
    room_id INTEGER,
    
    FOREIGN KEY(group_id) REFERENCES groups(id),
    FOREIGN KEY(week_id) REFERENCES weeks(id),
    FOREIGN KEY(teacher_id) REFERENCES teachers(id),
    FOREIGN KEY(room_id) REFERENCES rooms(id)
)
""")


conn.commit()
conn.close()
