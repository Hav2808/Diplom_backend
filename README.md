# Дипломный проект по профессии «Fullstack-разработчик на Python»
## Облачное хранилище My Cloud
### [Задание к диплому...](https://github.com/netology-code/fpy-diplom/blob/main/README.md)
## BACKEND
# Дополнительные библиотеки:
1. gunicorn [Документация](https://gunicorn.org/) - Для развертывания приложения
2. python-dotenv [Документация](https://pypi.org/project/python-dotenv/)
# Инструкци по сборке Django static files
## Шаг 1: Настройка settings.py
### Убедитесь, что у вас настроены следующие параметры в settings.py:
```python
# settings.py

import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

# URL для доступа к статическим файлам
STATIC_URL = '/static/'

# Директория, куда будут собираться все статические файлы
STATIC_ROOT = BASE_DIR / 'static'

# Директории с исходными статическими файлами сюда помещаем файлы из dist фронтенда
STATICFILES_DIRS = [
    BASE_DIR / 'staticfiles',
]
```
## Шаг 2: Настройка templates шаблона вашего проекта
### Создайте папку templates директории вашего django приложения, создайте файл с названием index.html где укажите следующий html код
```html
<!doctype html>
<html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>My Vite + React App</title>
        {% load static %} <!-- <Загрузка статики> -->
        <!-- <Название css файла в папке static> -->
        <link rel="stylesheet" href="/static/dist/assets/index-5r73d6Iz.css"> 
    </head>
    <body>
        <div id="root"></div>
        <!-- <Название js файла в папке static> -->
        <script src="/static/dist/assets/index-BYdkeK0M.js"></script>
    </body>
</html>
```
## Шаг 3: Настройка views.py вашего проекта
### Убедитесь, что у вас присутвует следующие код в представлениях:
```python
def index(request, *args, **kwargs):
    return render(request, 'index.html') #index.html из папки templates
```
## Шаг 4: Настройка urls.py вашего проекта
### Убедитесь, что у вас настроен следующий параметры в urls.py:
```python
urlpatterns = [
    ...
    re_path(r'^auth/', include('djoser.urls.authtoken')),
    re_path(r'^.*$', views.index, name='index'),
]
```
## Шаг 5: Сборка статических файлов
### Соберите все статические файлы из указанных директорий в STATIC_ROOT с помощью команды:
### Убедитесь что в папке staticfiles бэкэнда присутствуют файлы из папки dist(название может отличаться в зависимости от настроек build) вашего фронтенд.
После выполните:
```
python manage.py collectstatic
```
