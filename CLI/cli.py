import click
import logging

# Настраиваем логгер
logger = logging.getLogger(__name__)
handler = logging.StreamHandler()
formatter = logging.Formatter('[%(levelname)s] %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

@click.command()
@click.option('--group', '-g', required=True, help='Название группы, например ИУ7-75')
@click.option('--week', '-w', required=True, type=int, help='Номер недели (1–52)')
@click.option('--year', '-y', default=2025, type=int, help='Год (по умолчанию текущий)')
@click.option('--no-cache', is_flag=True, help='Отключить использование кэша')
@click.option('--debug', is_flag=True, help='Включить отладочный режим')
def main(group, week, year, no_cache, debug):
    """
    Загрузка расписания МАИ по параметрам группы, недели и года.
    """
    # Уровень логирования
    logger.setLevel(logging.DEBUG if debug else logging.INFO)

    # Проверка на валидность недели
    if not (1 <= week <= 52):
        logger.error("Номер недели должен быть от 1 до 52.")
        return

    logger.info(f"Группа: {group}")
    logger.info(f"Неделя: {week}")
    logger.info(f"Год: {year}")
    logger.info(f"Кэш выключен: {no_cache}")
    logger.debug("Режим отладки включён")

    try:
        # Здесь в будущем будет вызов ScheduleDownloader
        logger.info("Имитация загрузки расписания...")
        raw_data = f"<html>...</html>"  # Заглушка вместо реальных данных
        logger.debug(f"Полученные данные: {raw_data[:100]}...")  # Только первые 100 символов
    except Exception as e:
        logger.exception("Произошла ошибка при загрузке расписания")
        return

if __name__ == '__main__':
    main()
