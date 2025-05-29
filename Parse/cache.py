import os
import json
import hashlib
from datetime import datetime, timedelta

class FileCacheManager:
    def __init__(self, cache_dir="mai_cache", ttl_hours=24):
        self.cache_dir = cache_dir
        self.ttl = timedelta(hours=ttl_hours)
        
        if not os.path.exists(cache_dir):
            os.makedirs(cache_dir)
    
    def _get_cache_key(self, group_name, target_date=None, week_number=None):
        """Генерирует уникальный ключ для кэша"""
        key_str = f"{group_name}_{target_date}_{week_number}"
        return hashlib.md5(key_str.encode()).hexdigest()
    
    def _get_cache_path(self, key):
        return os.path.join(self.cache_dir, f"{key}.json")
    
    def get_cached_page(self, group_name, target_date=None, week_number=None):
        """Получает HTML из кэша если он есть и актуален"""
        key = self._get_cache_key(group_name, target_date, week_number)
        cache_file = self._get_cache_path(key)
        
        if not os.path.exists(cache_file):
            return None
            
        try:
            with open(cache_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            # Проверяем срок годности
            cache_time = datetime.fromisoformat(data['timestamp'])
            if datetime.now() - cache_time > self.ttl:
                self.logger.debug(f"Кэш устарел для {key}")
                return None
                
            return data['html']
        except Exception as e:
            self.logger.warning(f"Ошибка чтения кэша: {str(e)}")
            return None
    
    def save_to_cache(self, html, group_name, target_date=None, week_number=None):
        """Сохраняет HTML в кэш"""
        key = self._get_cache_key(group_name, target_date, week_number)
        cache_file = self._get_cache_path(key)
        
        data = {
            'html': html,
            'timestamp': datetime.now().isoformat(),
            'group': group_name,
            'date': target_date,
            'week': week_number
        }
        
        try:
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            self.logger.error(f"Ошибка сохранения в кэш: {str(e)}")
            return False
    
    def cleanup_expired(self):
        """Очищает устаревшие кэш-файлы"""
        now = datetime.now()
        deleted = 0
        
        for filename in os.listdir(self.cache_dir):
            filepath = os.path.join(self.cache_dir, filename)
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                cache_time = datetime.fromisoformat(data['timestamp'])
                if now - cache_time > self.ttl:
                    os.remove(filepath)
                    deleted += 1
            except:
                continue
                
        self.logger.info(f"Очищено устаревших файлов: {deleted}")
        return deleted


class MAIScheduleParser:
    def __init__(self, headless=False):
        self.base_url = "https://mai.ru/education/studies/schedule/"
        self.driver = None
        self.headless = headless
        self.cache = FileCacheManager()  # Инициализация кэш-менеджера
        self.setup_logger()
    
    def setup_logger(self):
        self.logger = logging.getLogger('mai_schedule')
        self.logger.setLevel(logging.DEBUG)
        handler = logging.StreamHandler()
        handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
        self.logger.addHandler(handler)
    
    def get_page_html(self):
        """Получает HTML текущей страницы"""
        try:
            WebDriverWait(self.driver, 30).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "ul.step"))
            return self.driver.page_source
        except Exception as e:
            self.logger.error(f"Ошибка получения HTML: {str(e)}")
            return None
    
    def get_schedule(self, group_name, target_date=None, week_number=None):
        """Основной метод получения расписания с кэшированием"""
        try:
            # Пробуем получить из кэша
            cached_html = self.cache.get_cached_page(group_name, target_date, week_number)
            if cached_html:
                self.logger.info("Используем закешированную версию страницы")
                self.driver = None  # Не инициализируем браузер
                return self.parse_html(cached_html)
            
            # Если нет в кэше - загружаем через браузер
            if not self.init_driver():
                return None
                
            self.driver.get(self.base_url)
            time.sleep(3)
            
            if not self.select_institute_and_course():
                return None
                
            sections = [
                "Базовое высшее образование",
                "Специализированное высшее образование",
                "Аспирантура"
            ]
            
            for section in sections:
                if self.select_education_type(section):
                    if self.find_and_select_group(group_name):
                        if target_date:
                            if not self.select_week_by_date(target_date):
                                continue
                        elif week_number is not None:
                            if not self.select_week(week_number):
                                continue
                        
                        time.sleep(3)
                        html = self.get_page_html()
                        if html:
                            # Сохраняем в кэш перед парсингом
                            self.cache.save_to_cache(html, group_name, target_date, week_number)
                            return self.parse_html(html)
            
            self.logger.error(f"Группа {group_name} не найдена ни в одном разделе")
            return None
            
        except Exception as e:
            self.logger.error(f"Неожиданная ошибка: {str(e)}")
            return None
        finally:
            if self.driver:
                self.driver.quit()
    
    def parse_html(self, html):
        """Парсит расписание из HTML (аналогично оригинальному parse_schedule)"""
        # Здесь должна быть реализация парсинга из HTML
        # Можно использовать BeautifulSoup вместо Selenium
        pass