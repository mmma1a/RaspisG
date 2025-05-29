from bs4 import BeautifulSoup
import json
import re
from datetime import datetime
import pandas as pd
from typing import Dict, List, Union, Optional

class ScheduleParser:
    def __init__(self):
        self.logger = logging.getLogger('mai_schedule.parser')
        
    def parse_html(self, html_content: str) -> Optional[pd.DataFrame]:
        """Парсинг HTML страницы с расписанием"""
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            week_title = self._extract_week_title(soup)
            schedule_data = []
            
            # Парсим каждый день недели
            day_elements = soup.select('ul.step li.step-item')
            for day in day_elements:
                day_data = self._parse_day(day, week_title)
                schedule_data.extend(day_data)
                
            return self._create_dataframe(schedule_data)
            
        except Exception as e:
            self.logger.error(f"Ошибка парсинга HTML: {str(e)}")
            return None
    
    def parse_json(self, json_data: Union[dict, str]) -> Optional[pd.DataFrame]:
        """Парсинг JSON данных с расписанием"""
        try:
            if isinstance(json_data, str):
                json_data = json.loads(json_data)
                
            schedule_data = []
            
            for day in json_data.get('days', []):
                date = day.get('date')
                day_name = day.get('day_name')
                
                for lesson in day.get('lessons', []):
                    lesson_data = {
                        'Дата': date,
                        'День недели': day_name,
                        'Время': self._normalize_time(lesson.get('time')),
                        'Дисциплина': lesson.get('subject'),
                        'Тип занятия': lesson.get('type'),
                        'Преподаватель': self._normalize_teacher(lesson.get('teacher')),
                        'Аудитория': self._normalize_room(lesson.get('room'))
                    }
                    schedule_data.append(lesson_data)
                    
            return self._create_dataframe(schedule_data)
            
        except Exception as e:
            self.logger.error(f"Ошибка парсинга JSON: {str(e)}")
            return None
    
    def _extract_week_title(self, soup: BeautifulSoup) -> Dict[str, str]:
        """Извлекает информацию о неделе из заголовка"""
        try:
            title = soup.select_one('h1.schedule-title').text
            start_str, end_str = title.split(' - ')
            return {
                'start_date': datetime.strptime(start_str.strip(), "%d.%m.%Y"),
                'end_date': datetime.strptime(end_str.strip(), "%d.%m.%Y"),
                'title': title.strip()
            }
        except:
            return {}
    
    def _parse_day(self, day_element, week_info: Dict) -> List[Dict]:
        """Парсит один день расписания"""
        try:
            date_element = day_element.select_one('span.step-title')
            date_text = date_element.text.strip() if date_element else "Не указана"
            
            lessons = day_element.select('div.step-content > div.mb-4')
            day_data = []
            
            if not lessons:
                # День без занятий
                return [{
                    'Дата': date_text,
                    'День недели': date_text.split(',')[0].strip() if ',' in date_text else date_text,
                    'Время': "",
                    'Дисциплина': "Нет занятий",
                    'Тип занятия': "",
                    'Преподаватель': "",
                    'Аудитория': ""
                }]
            
            for lesson in lessons:
                try:
                    subject = lesson.select_one('p.fw-semi-bold').text.strip()
                    lesson_type = lesson.select_one('span.badge').text.strip()
                    details = lesson.select('ul.list-inline li.list-inline-item')
                    
                    lesson_data = {
                        'Дата': date_text,
                        'День недели': date_text.split(',')[0].strip() if ',' in date_text else date_text,
                        'Время': self._normalize_time(details[0].text.strip() if len(details) > 0 else ""),
                        'Дисциплина': subject,
                        'Тип занятия': lesson_type,
                        'Преподаватель': self._normalize_teacher(details[1].text.strip() if len(details) > 1 else ""),
                        'Аудитория': self._normalize_room(details[2].text.strip() if len(details) > 2 else "")
                    }
                    day_data.append(lesson_data)
                except Exception as e:
                    self.logger.warning(f"Ошибка парсинга занятия: {str(e)}")
                    continue
                    
            return day_data
            
        except Exception as e:
            self.logger.error(f"Ошибка парсинга дня: {str(e)}")
            return []
    
    def _create_dataframe(self, data: List[Dict]) -> pd.DataFrame:
        """Создает DataFrame и выполняет валидацию"""
        df = pd.DataFrame(data)
        
        # Удаление дубликатов
        df = df.drop_duplicates()
        
        # Сортировка по дате и времени
        try:
            df['Дата'] = pd.to_datetime(df['Дата'], format='%a, %d %B', errors='ignore')
            df.sort_values(by=['Дата', 'Время'], inplace=True)
            df['Дата'] = df['Дата'].dt.strftime('%a, %d %B')
        except:
            df.sort_values(by=['Дата', 'Время'], inplace=True)
            
        return df
    
    def _normalize_time(self, time_str: str) -> str:
        """Нормализация формата времени"""
        if not time_str:
            return ""
            
        # Приводим к формату "HH:MM-HH:MM"
        time_str = re.sub(r'[^\d:-]', '', time_str)
        time_str = re.sub(r'(\d{1,2})([:]?)(\d{2})', r'\1:\3', time_str)
        return time_str.strip()
    
    def _normalize_teacher(self, teacher: str) -> str:
        """Нормализация ФИО преподавателя"""
        if not teacher:
            return "Не указан"
            
        # Удаляем лишние пробелы и приводим к формату "Фамилия И.О."
        teacher = re.sub(r'\s+', ' ', teacher).strip()
        parts = teacher.split()
        if len(parts) >= 3:
            return f"{parts[0]} {parts[1][0]}.{parts[2][0]}."
        return teacher
    
    def _normalize_room(self, room: str) -> str:
        """Нормализация названия аудитории"""
        if not room:
            return "Не указана"
            
        # Удаляем лишние пробелы и приводим к верхнему регистру
        room = re.sub(r'\s+', ' ', room).strip().upper()
        return room