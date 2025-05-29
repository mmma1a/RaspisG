from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from typing import List, Dict, Optional
from .static_data import INSTITUTES, GROUPS, get_schedule
import os

app = FastAPI(title="MAI Schedule")

# Настройка CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Получаем абсолютный путь к директории frontend
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
FRONTEND_DIR = os.path.join(BASE_DIR, "frontend")

# Монтируем статические файлы
app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")

@app.get("/", response_class=HTMLResponse)
async def get_index():
    """Главная страница"""
    with open(os.path.join(FRONTEND_DIR, "index.html"), "r", encoding="utf-8") as f:
        return f.read()

@app.get("/institute/{institute_id}", response_class=HTMLResponse)
async def get_institute_page(institute_id: str):
    """Страница института"""
    if institute_id not in GROUPS:
        raise HTTPException(status_code=404, detail=f"Институт с ID {institute_id} не найден")
    
    with open(os.path.join(FRONTEND_DIR, "index.html"), "r", encoding="utf-8") as f:
        content = f.read()
        # Здесь можно добавить динамическую генерацию HTML для конкретного института
        return content

@app.get("/group/{group_id}", response_class=HTMLResponse)
async def get_group_page(group_id: str):
    """Страница группы"""
    schedule = get_schedule(group_id)
    if not schedule:
        raise HTTPException(status_code=404, detail=f"Группа {group_id} не найдена")
    
    with open(os.path.join(FRONTEND_DIR, "index.html"), "r", encoding="utf-8") as f:
        content = f.read()
        # Здесь можно добавить динамическую генерацию HTML для конкретной группы
        return content

# Оставляем API endpoints для возможного использования в будущем
@app.get("/api/institutes")
async def get_institutes():
    """Получение списка институтов"""
    return INSTITUTES

@app.get("/api/groups/{institute_id}")
async def get_groups(institute_id: str, course: Optional[int] = None):
    """Получение списка групп для института"""
    if institute_id not in GROUPS:
        raise HTTPException(status_code=404, detail=f"Институт с ID {institute_id} не найден")
        
    if course:
        course_str = str(course)
        if course_str in GROUPS[institute_id]:
            return GROUPS[institute_id][course_str]
        else:
            raise HTTPException(status_code=404, detail=f"Курс {course} не найден в институте {institute_id}")
    
    # Если курс не указан, возвращаем все группы института
    all_groups = []
    for course_groups in GROUPS[institute_id].values():
        all_groups.extend(course_groups)
    return all_groups

@app.get("/api/schedule/{group_id}")
async def get_schedule_endpoint(group_id: str):
    """Получение расписания для группы"""
    return get_schedule(group_id) 