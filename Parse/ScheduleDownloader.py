import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import logging
import pandas as pd
from datetime import datetime

class MAIScheduleParser:
    def __init__(self, headless=False):
        self.base_url = "https://mai.ru/education/studies/schedule/"
        self.driver = None
        self.headless = headless
        self.setup_logger()
    
    def setup_logger(self):
        self.logger = logging.getLogger('mai_schedule')
        self.logger.setLevel(logging.DEBUG)
        handler = logging.StreamHandler()
        handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
        self.logger.addHandler(handler)
    
    def init_driver(self):
        try:
            options = webdriver.ChromeOptions()
            if self.headless:
                options.add_argument('--headless')
            options.add_argument('--disable-blink-features=AutomationControlled')
            options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
            options.add_argument('--window-size=1920,1080')
            options.add_experimental_option("excludeSwitches", ["enable-automation"])
            options.add_experimental_option('useAutomationExtension', False)
            
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=options)
            self.driver.set_page_load_timeout(60)
            self.logger.info("Браузер успешно запущен")
            return True
        except Exception as e:
            self.logger.error(f"Ошибка инициализации браузера: {str(e)}")
            return False

    def select_institute_and_course(self):
        """Выбираем институт №8 и курс"""
        try:
            WebDriverWait(self.driver, 30).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "form")))
            
            institute_select = self.driver.find_element(By.CSS_SELECTOR, "select#department")
            self.driver.execute_script("""
                const select = arguments[0];
                for (let i = 0; i < select.options.length; i++) {
                    if (select.options[i].text.includes('Институт №8')) {
                        select.selectedIndex = i;
                        select.dispatchEvent(new Event('change', {bubbles: true}));
                        break;
                    }
                }
            """, institute_select)
            time.sleep(2)
            
            course_select = self.driver.find_element(By.CSS_SELECTOR, "select#course")
            self.driver.execute_script("""
                arguments[0].value = '1';
                arguments[0].dispatchEvent(new Event('change', {bubbles: true}));
            """, course_select)
            time.sleep(2)
            
            show_btn = self.driver.find_element(By.CSS_SELECTOR, "button.btn-primary")
            self.driver.execute_script("arguments[0].click();", show_btn)
            time.sleep(5)
            
            self.logger.info("Институт №8 и 1 курс выбраны")
            return True
        except Exception as e:
            self.logger.error(f"Ошибка выбора института/курса: {str(e)}")
            return False

    def select_education_type(self, section_name):
        """Выбираем тип образования"""
        try:
            tab = self.driver.find_element(By.XPATH, f"//a[contains(@class, 'nav-link') and contains(., '{section_name}')]")
            self.driver.execute_script("arguments[0].click();", tab)
            time.sleep(3)
            return True
        except Exception as e:
            self.logger.error(f"Ошибка выбора типа образования '{section_name}': {str(e)}")
            return False

    def find_and_select_group(self, group_name):
        """Ищем и выбираем группу"""
        try:
            variants = [
                group_name,
                group_name.replace("М8О", "№80"),
                group_name.replace("М8О", "№80").replace("БВ", "5B"),
                group_name.replace("М8О", "№80").replace("БВ", "5B-24"),
                group_name.replace("М8О", "№80").replace("БВ", "5B")
            ]
            
            for variant in variants:
                try:
                    group_element = self.driver.find_element(By.XPATH, f"//*[contains(text(), '{variant}')]")
                    self.driver.execute_script("arguments[0].scrollIntoView(); arguments[0].click();", group_element)
                    time.sleep(3)
                    self.logger.info(f"Группа найдена как: {variant}")
                    return True
                except:
                    continue
            
            self.logger.info("Группа не найдена")
            return False
        except Exception as e:
            self.logger.error(f"Ошибка поиска группы: {str(e)}")
            return False

    def select_week_by_date(self, input_date):
        """Выбираем учебную неделю по дате"""
        try:
            # Парсим введенную дату
            try:
                target_date = datetime.strptime(input_date, "%d.%m.%Y").date()
            except ValueError:
                self.logger.error("Неверный формат даты. Используйте DD.MM.YYYY")
                return False
            
            # Ждем и кликаем кнопку выбора недели
            try:
                week_button = WebDriverWait(self.driver, 20).until(
                    EC.element_to_be_clickable(
                        (By.XPATH, "//a[contains(@class, 'btn') and contains(., 'Выбрать учебную неделю')]")
                    )
                )
                self.driver.execute_script("arguments[0].scrollIntoView(); arguments[0].click();", week_button)
                time.sleep(2)
            except Exception as e:
                self.logger.error(f"Ошибка при клике на кнопку выбора недели: {str(e)}")
                return False
            
            # Ждем появления списка недель
            try:
                WebDriverWait(self.driver, 20).until(
                    EC.visibility_of_element_located(
                        (By.CSS_SELECTOR, "div.collapse.show#collapseWeeks")
                    )
                )
                time.sleep(1)
            except Exception as e:
                self.logger.error(f"Список недель не появился: {str(e)}")
                return False
            
            # Находим все элементы недель
            try:
                week_items = self.driver.find_elements(
                    By.CSS_SELECTOR, "div#collapseWeeks li.list-group-item")
                
                if not week_items:
                    self.logger.error("Не найдены элементы недель в списке")
                    return False
                    
            except Exception as e:
                self.logger.error(f"Ошибка при поиске элементов недель: {str(e)}")
                return False
            
            # Ищем нужную неделю
            found_week = None
            week_info = None
            
            for item in week_items:
                try:
                    date_span = item.find_element(By.CSS_SELECTOR, "span.d-block")
                    week_text = date_span.text.strip()
                    
                    # Парсим даты недели
                    start_str, end_str = week_text.split(' - ')
                    start_date = datetime.strptime(start_str.strip(), "%d.%m.%Y").date()
                    end_date = datetime.strptime(end_str.strip(), "%d.%m.%Y").date()
                    
                    if start_date <= target_date <= end_date:
                        week_link = item.find_element(By.TAG_NAME, "a")
                        week_info = {
                            'text': week_text,
                            'element': week_link,
                            'href': week_link.get_attribute('href')
                        }
                        found_week = week_info
                        break
                        
                except Exception as e:
                    self.logger.warning(f"Ошибка обработки элемента недели: {str(e)}")
                    continue
            
            if not found_week:
                self.logger.error(f"Не найдена неделя, содержащая дату {input_date}")
                return False
                
            # Выбираем неделю
            try:
                # Сохраняем текущий URL для проверки изменений
                current_url = self.driver.current_url
                
                # Используем JavaScript для перехода по ссылке
                self.driver.execute_script(f"window.location.href = '{found_week['href']}';")
                
                # Ждем изменения URL или загрузки расписания
                WebDriverWait(self.driver, 20).until(
                    lambda d: d.current_url != current_url or 
                    d.find_elements(By.CSS_SELECTOR, "ul.step li.step-item")
                )
                
                # Дополнительная проверка загрузки
                WebDriverWait(self.driver, 20).until(
                    EC.presence_of_element_located(
                        (By.CSS_SELECTOR, "ul.step li.step-item")
                    )
                )
                
                self.logger.info(f"Успешно выбрана неделя: {found_week['text']}")
                return True
                
            except Exception as e:
                self.logger.error(f"Ошибка при выборе недели: {str(e)}")
                return False
                
        except Exception as e:
            self.logger.error(f"Неожиданная ошибка при выборе недели: {str(e)}")
            return False

    def parse_schedule(self):
        """Парсим расписание всей недели, включая пустые дни"""
        try:
            # Ждем загрузки всего расписания недели
            WebDriverWait(self.driver, 30).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "ul.step"))
            )
            time.sleep(3)  # Увеличили задержку для полной загрузки
            
            # Получаем диапазон дат недели из заголовка
            try:
                week_title = self.driver.find_element(By.CSS_SELECTOR, "h1.schedule-title").text
                start_date_str, end_date_str = week_title.split(" - ")
                start_date = datetime.strptime(start_date_str.strip(), "%d.%m.%Y").date()
                end_date = datetime.strptime(end_date_str.strip(), "%d.%m.%Y").date()
                self.logger.info(f"Диапазон недели: {start_date_str} - {end_date_str}")
            except Exception as e:
                self.logger.warning(f"Не удалось определить диапазон недели: {str(e)}")
                start_date = end_date = None
            
            schedule = []
            
            # Находим все дни недели (даже если они без занятий)
            days = self.driver.find_elements(By.CSS_SELECTOR, "ul.step li.step-item")
            self.logger.debug(f"Найдено дней в интерфейсе: {len(days)}")
            
            # Если дней меньше 7, добавляем недостающие
            if start_date and end_date and len(days) < 7:
                all_dates = pd.date_range(start=start_date, end=end_date)
                existing_dates = []
                
                for day in days:
                    try:
                        date_text = day.find_element(By.CSS_SELECTOR, "span.step-title").text
                        existing_dates.append(date_text)
                    except:
                        continue
                
                # Добавляем пустые дни для отсутствующих дат
                for date in all_dates:
                    date_str = date.strftime("%a, %d %B")
                    if date_str not in existing_dates:
                        empty_day = {
                            'Дата': date_str,
                            'День недели': date.strftime("%a"),
                            'Время': "",
                            'Дисциплина': "Нет занятий",
                            'Тип занятия': "",
                            'Преподаватель': "",
                            'Аудитория': ""
                        }
                        schedule.append(empty_day)
            
            # Парсим все найденные дни
            for day in days:
                try:
                    # Извлекаем дату дня
                    try:
                        date_element = day.find_element(By.CSS_SELECTOR, "span.step-title")
                        date = date_element.text.strip()
                        self.logger.debug(f"Обрабатываем день: {date}")
                    except:
                        date = "Не указана"
                    
                    # Находим все занятия в этот день
                    lessons = day.find_elements(By.CSS_SELECTOR, "div.step-content > div.mb-4")
                    
                    if not lessons:
                        # Добавляем запись для дня без занятий
                        empty_day = {
                            'Дата': date,
                            'День недели': date.split(',')[0].strip() if ',' in date else date,
                            'Время': "",
                            'Дисциплина': "Нет занятий",
                            'Тип занятия': "",
                            'Преподаватель': "",
                            'Аудитория': ""
                        }
                        schedule.append(empty_day)
                        continue
                    
                    for lesson in lessons:
                        try:
                            subject = lesson.find_element(By.CSS_SELECTOR, "p.fw-semi-bold").text.strip()
                            lesson_type = lesson.find_element(By.CSS_SELECTOR, "span.badge").text.strip()
                            details = lesson.find_elements(By.CSS_SELECTOR, "ul.list-inline li.list-inline-item")
                            
                            lesson_data = {
                                'Дата': date,
                                'День недели': date.split(',')[0].strip() if ',' in date else date,
                                'Время': details[0].text.strip() if len(details) > 0 else "Не указано",
                                'Дисциплина': subject,
                                'Тип занятия': lesson_type,
                                'Преподаватель': details[1].text.strip() if len(details) > 1 else "Не указан",
                                'Аудитория': details[2].text.strip() if len(details) > 2 else "Не указана"
                            }
                            schedule.append(lesson_data)
                        except Exception as e:
                            self.logger.warning(f"Ошибка парсинга занятия: {str(e)}")
                            continue
                            
                except Exception as e:
                    self.logger.warning(f"Ошибка обработки дня: {str(e)}")
                    continue
            
            # Создаем DataFrame и сортируем
            df = pd.DataFrame(schedule)
            
            # Преобразуем даты для правильной сортировки
            try:
                df['Дата'] = pd.to_datetime(df['Дата'], format='%a, %d %B', errors='ignore')
                df.sort_values(by=['Дата', 'Время'], inplace=True)
                # Возвращаем даты в читаемый формат
                df['Дата'] = df['Дата'].dt.strftime('%a, %d %B')
            except:
                df.sort_values(by=['Дата', 'Время'], inplace=True)
            
            self.logger.info(f"Успешно получено расписание на {len(df)} занятий")
            return df
            
        except Exception as e:
            self.logger.error(f"Ошибка парсинга расписания: {str(e)}")
            try:
                self.driver.save_screenshot('parse_error.png')
                self.logger.info("Скриншот сохранен как parse_error.png")
            except:
                pass
            return None

    def get_schedule(self, group_name, target_date=None, week_number=None):
        """Основной метод получения расписания"""
        try:
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
                        
                        # Добавляем дополнительное ожидание перед парсингом
                        time.sleep(3)
                        schedule_df = self.parse_schedule()
                        
                        if schedule_df is not None:
                            # Проверяем, что получили все дни недели
                            if len(schedule_df['Дата'].unique()) < 7:
                                self.logger.warning("В расписании присутствуют не все дни недели")
                            return schedule_df
            
            self.logger.error(f"Группа {group_name} не найдена ни в одном разделе")
            return None
            
        except Exception as e:
            self.logger.error(f"Неожиданная ошибка: {str(e)}")
            return None
        finally:
            if self.driver:
                self.driver.quit()

if __name__ == "__main__":
    print("=== Парсер расписания МАИ (полная версия) ===")
    
    group_name = input("Введите номер группы: ").strip()
    date_input = input("Введите дату в формате DD.MM.YYYY (например, 12.02.2025): ").strip()
    week_number = None
    
    if not date_input:
        week_input = input("Введите номер учебной недели (1-18, оставьте пустым для текущей недели): ").strip()
        try:
            week_number = int(week_input) if week_input else None
            if week_number is not None and (week_number < 1 or week_number > 18):
                print("Номер недели должен быть от 1 до 18")
                exit()
        except ValueError:
            print("Номер недели должен быть числом")
            exit()
    
    parser = MAIScheduleParser(headless=False)
    schedule = parser.get_schedule(group_name, target_date=date_input if date_input else None, week_number=week_number)
    
    if schedule is not None and not schedule.empty:
        if date_input:
            filename = f"расписание_{group_name}_{date_input.replace('.', '-')}.xlsx"
        else:
            week_suffix = f"_неделя_{week_number}" if week_number else ""
            filename = f"расписание_{group_name}{week_suffix}.xlsx"
            
        schedule.to_excel(filename, index=False)
        print(f"\nРасписание сохранено в файл: {filename}")
        print("\nПервые занятия:")
        print(schedule.head())
        
        # Проверяем наличие всех дней недели
        unique_days = schedule['Дата'].nunique()
        if unique_days < 7:
            print(f"\nВнимание: в расписании только {unique_days} дней из 7. Возможно, некоторые дни не содержат занятий.")
    else:
        print("\nНе удалось получить расписание.")