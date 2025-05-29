import aiohttp
from bs4 import BeautifulSoup
from typing import Dict, List, Optional
import json
import re

class MAIParser:
    BASE_URL = "https://mai.ru/education/studies/schedule/groups.php"
    
    def __init__(self):
        self.session = None
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
            
    async def get_institutes(self) -> List[Dict[str, str]]:
        """Получение списка институтов"""
        async with self.session.get(self.BASE_URL) as response:
            html = await response.text()
            
        soup = BeautifulSoup(html, 'html.parser')
        institute_select = soup.find('select', {'name': 'institute'})
        
        if not institute_select:
            return []
            
        institutes = []
        for option in institute_select.find_all('option'):
            if option.get('value') and option.text.strip():
                institutes.append({
                    'id': option['value'],
                    'name': option.text.strip()
                })
                
        return institutes
        
    async def get_groups(self, institute_id: str, course: Optional[int] = None) -> List[Dict[str, str]]:
        """Получение списка групп для института и курса"""
        params = {'institute': institute_id}
        if course:
            params['course'] = str(course)
            
        async with self.session.get(self.BASE_URL, params=params) as response:
            html = await response.text()
            
        soup = BeautifulSoup(html, 'html.parser')
        group_select = soup.find('select', {'name': 'group'})
        
        if not group_select:
            return []
            
        groups = []
        for option in group_select.find_all('option'):
            if option.get('value') and option.text.strip():
                group_name = option.text.strip()
                # Извлекаем номер курса из названия группы
                course_match = re.search(r'(\d+)', group_name)
                course_number = int(course_match.group(1)) if course_match else None
                
                groups.append({
                    'id': option['value'],
                    'name': group_name,
                    'course': course_number
                })
                
        return groups
        
    async def get_schedule(self, group_id: str) -> Dict:
        """Получение расписания для группы"""
        params = {'group': group_id}
        
        async with self.session.get(self.BASE_URL, params=params) as response:
            html = await response.text()
            
        soup = BeautifulSoup(html, 'html.parser')
        schedule_table = soup.find('table', {'class': 'schedule'})
        
        if not schedule_table:
            return {'error': 'Расписание не найдено'}
            
        schedule = {
            'monday': [],
            'tuesday': [],
            'wednesday': [],
            'thursday': [],
            'friday': [],
            'saturday': [],
            'sunday': []
        }
        
        current_day = None
        for row in schedule_table.find_all('tr'):
            # Проверяем, является ли строка заголовком дня
            day_header = row.find('th', {'colspan': '4'})
            if day_header:
                day_name = day_header.text.strip().lower()
                current_day = day_name
                continue
                
            if current_day and row.find_all('td'):
                cells = row.find_all('td')
                if len(cells) >= 4:
                    lesson = {
                        'time': cells[0].text.strip(),
                        'name': cells[1].text.strip(),
                        'teacher': cells[2].text.strip(),
                        'room': cells[3].text.strip()
                    }
                    schedule[current_day].append(lesson)
                    
        return schedule 