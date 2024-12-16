import random
import uuid
from datetime import datetime
import pytz

def user_directory_path(instance, filename):
    """
    Функция для динамического определения пути для сохранения файла
    """
    return 'user_{0}/{1}'.format(instance.creator.id, filename)

def seconds_since_epoch():
    """
    Функция для получения времени в секндах с начала эпохи
    """
    moscow_tz = pytz.timezone('Europe/Moscow')
    current_time = datetime.now(moscow_tz)
    return int(current_time.timestamp())

def generating_uuid():
    """
    Функция для получения уникального индентификатора
    """
    return uuid.uuid1(random.randint(10, 10**12))