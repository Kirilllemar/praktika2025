# 🚀 Полное руководство по переносу системы управления кафе в другой репозиторий

Данное руководство содержит пошаговые инструкции по переносу системы управления кафе из текущего репозитория в новый репозиторий с сохранением всех функций и данных.

## 📋 Содержание

1. [Подготовка к переносу](#подготовка-к-переносу)
2. [Создание нового репозитория](#создание-нового-репозитория)
3. [Перенос файлов](#перенос-файлов)
4. [Настройка окружения](#настройка-окружения)
5. [Первый запуск](#первый-запуск)
6. [Миграция данных](#миграция-данных)
7. [Настройка для продакшена](#настройка-для-продакшена)
8. [Возможные проблемы](#возможные-проблемы)
9. [Дополнительные настройки](#дополнительные-настройки)
10. [Тестирование](#тестирование)

## 📦 Подготовка к переносу

### Шаг 1: Создание архива системы

```bash
# Перейдите в директорию с системой
cd /path/to/current/cafe-system

# Создайте архив всех файлов (исключая служебные)
tar -czf cafe-management-system.tar.gz \
  --exclude='.git' \
  --exclude='__pycache__' \
  --exclude='*.pyc' \
  --exclude='venv' \
  --exclude='node_modules' \
  --exclude='.env' \
  .

# Или используйте zip
zip -r cafe-management-system.zip . \
  -x '.git/*' '__pycache__/*' '*.pyc' 'venv/*' 'node_modules/*' '.env'
```

### Шаг 2: Создание списка файлов для переноса

```bash
# Создайте список всех файлов проекта
find . -type f \
  -not -path './.git/*' \
  -not -path './venv/*' \
  -not -path './__pycache__/*' \
  -not -name '*.pyc' \
  > files_to_transfer.txt

# Просмотрите список
cat files_to_transfer.txt
```

### Шаг 3: Создание резервной копии данных

```bash
# Если у вас есть существующая база данных
cp cafe_system.db cafe_system_backup.db

# Создайте dump базы данных (если используете SQLite)
sqlite3 cafe_system.db ".dump" > cafe_system_dump.sql

# Или используйте Python для экспорта данных
python3 -c "
import sqlite3
import json
import os

if os.path.exists('cafe_system.db'):
    conn = sqlite3.connect('cafe_system.db')
    cursor = conn.cursor()
    
    # Получите список всех таблиц
    cursor.execute(\"SELECT name FROM sqlite_master WHERE type='table'\")
    tables = cursor.fetchall()
    
    backup_data = {}
    for table in tables:
        table_name = table[0]
        cursor.execute(f'SELECT * FROM {table_name}')
        rows = cursor.fetchall()
        cursor.execute(f'PRAGMA table_info({table_name})')
        columns = [col[1] for col in cursor.fetchall()]
        backup_data[table_name] = {
            'columns': columns,
            'data': rows
        }
    
    with open('database_backup.json', 'w', encoding='utf-8') as f:
        json.dump(backup_data, f, indent=2, ensure_ascii=False, default=str)
    
    conn.close()
    print('Резервная копия данных создана: database_backup.json')
else:
    print('База данных не найдена')
"
```

## 🆕 Создание нового репозитория

### Вариант 1: Через GitHub веб-интерфейс

1. **Войдите в GitHub** и нажмите кнопку "New repository"
2. **Заполните форму:**
   - Repository name: `cafe-management-system`
   - Description: `Информационная система управления кафе`
   - Privacy: Public/Private (по выбору)
   - ✅ Add a README file
   - ✅ Add .gitignore (выберите Python)
   - ✅ Choose a license (рекомендуется MIT)

3. **Нажмите "Create repository"**

### Вариант 2: Через GitHub CLI

```bash
# Установите GitHub CLI (если не установлен)
# Ubuntu/Debian:
sudo apt install gh

# macOS:
brew install gh

# Windows (через Chocolatey):
choco install gh

# Авторизуйтесь в GitHub
gh auth login

# Создайте новый репозиторий
gh repo create cafe-management-system \
  --public \
  --description "Информационная система управления кафе" \
  --gitignore Python \
  --license MIT \
  --clone
```

### Вариант 3: Через Git командную строку

```bash
# Создайте новую директорию для проекта
mkdir cafe-management-system
cd cafe-management-system

# Инициализируйте Git репозиторий
git init

# Создайте файл README
echo "# Система управления кафе" > README.md

# Добавьте и зафиксируйте начальный коммит
git add README.md
git commit -m "Initial commit"

# Добавьте remote origin (замените на ваш URL)
git remote add origin https://github.com/yourusername/cafe-management-system.git

# Отправьте в удаленный репозиторий
git push -u origin main
```

## 📂 Перенос файлов

### Метод 1: Прямое копирование

```bash
# Перейдите в новую директорию проекта
cd /path/to/new/cafe-management-system

# Скопируйте все файлы из старого проекта
cp -r /path/to/old/cafe-system/* .

# Или используйте rsync для более точного копирования
rsync -av \
  --exclude='.git' \
  --exclude='__pycache__' \
  --exclude='*.pyc' \
  --exclude='venv' \
  --exclude='.env' \
  /path/to/old/cafe-system/ .

# Проверьте скопированные файлы
ls -la
```

### Метод 2: Через архив

```bash
# Распакуйте созданный ранее архив
tar -xzf cafe-management-system.tar.gz

# Или для zip
unzip cafe-management-system.zip
```

### Метод 3: Клонирование структуры

```bash
# Создайте структуру директорий
mkdir -p templates static/css static/js

# Скопируйте файлы по группам
cp /path/to/old/cafe-system/*.py .
cp /path/to/old/cafe-system/*.txt .
cp /path/to/old/cafe-system/*.md .
cp /path/to/old/cafe-system/templates/* templates/
cp /path/to/old/cafe-system/static/css/* static/css/
cp /path/to/old/cafe-system/static/js/* static/js/
```

## 🔧 Настройка окружения

### Шаг 1: Создание .gitignore

```bash
# Создайте файл .gitignore
cat > .gitignore << 'EOF'
# Byte-compiled / optimized / DLL files
__pycache__/
*.py[cod]
*$py.class

# C extensions
*.so

# Distribution / packaging
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
pip-wheel-metadata/
share/python-wheels/
*.egg-info/
.installed.cfg
*.egg
MANIFEST

# PyInstaller
*.manifest
*.spec

# Installer logs
pip-log.txt
pip-delete-this-directory.txt

# Unit test / coverage reports
htmlcov/
.tox/
.nox/
.coverage
.coverage.*
.cache
nosetests.xml
coverage.xml
*.cover
*.py,cover
.hypothesis/
.pytest_cache/

# Translations
*.mo
*.pot

# Django stuff:
*.log
local_settings.py
db.sqlite3
db.sqlite3-journal

# Flask stuff:
instance/
.webassets-cache

# Scrapy stuff:
.scrapy

# Sphinx documentation
docs/_build/

# PyBuilder
target/

# Jupyter Notebook
.ipynb_checkpoints

# IPython
profile_default/
ipython_config.py

# pyenv
.python-version

# pipenv
Pipfile.lock

# PEP 582
__pypackages__/

# Celery stuff
celerybeat-schedule
celerybeat.pid

# SageMath parsed files
*.sage.py

# Environments
.env
.venv
env/
venv/
ENV/
env.bak/
venv.bak/

# Spyder project settings
.spyderproject
.spyproject

# Rope project settings
.ropeproject

# mkdocs documentation
/site

# mypy
.mypy_cache/
.dmypy.json
dmypy.json

# Pyre type checker
.pyre/

# Специфичные для проекта
cafe_system.db
database_backup.json
*.db
*.db-journal
uploads/
logs/
EOF
```

### Шаг 2: Создание виртуального окружения

```bash
# Создайте виртуальное окружение
python3 -m venv venv

# Активируйте виртуальное окружение
# Linux/macOS:
source venv/bin/activate

# Windows:
venv\Scripts\activate

# Обновите pip
pip install --upgrade pip

# Установите зависимости
pip install -r requirements.txt

# Создайте файл requirements-dev.txt для разработки
cat > requirements-dev.txt << 'EOF'
# Основные зависимости
-r requirements.txt

# Инструменты разработки
pytest==7.4.3
pytest-flask==1.2.0
pytest-cov==4.1.0
black==23.10.1
flake8==6.1.0
isort==5.12.0
mypy==1.6.1
pre-commit==3.5.0
python-dotenv==1.0.0
EOF
```

### Шаг 3: Настройка переменных окружения

```bash
# Создайте файл .env для локальных настроек
cat > .env.example << 'EOF'
# Настройки Flask
FLASK_APP=app.py
FLASK_ENV=development
FLASK_DEBUG=True

# Секретный ключ (измените на свой)
SECRET_KEY=your-secret-key-here

# Настройки базы данных
DATABASE_URL=sqlite:///cafe_system.db

# Настройки сервера
HOST=0.0.0.0
PORT=5000

# Настройки почты (если используется)
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password

# Настройки загрузки файлов
UPLOAD_FOLDER=uploads
MAX_CONTENT_LENGTH=16777216

# Настройки логирования
LOG_LEVEL=INFO
LOG_FILE=app.log
EOF

# Скопируйте пример в рабочий файл
cp .env.example .env

# Отредактируйте .env под ваши нужды
nano .env  # или vim .env
```

## 🚀 Первый запуск

### Шаг 1: Проверка файлов

```bash
# Проверьте структуру проекта
tree -I 'venv|__pycache__|*.pyc'

# Или используйте ls
find . -type f -name "*.py" -o -name "*.html" -o -name "*.css" -o -name "*.js" | sort

# Проверьте права доступа
ls -la *.py
```

### Шаг 2: Инициализация базы данных

```bash
# Активируйте виртуальное окружение
source venv/bin/activate

# Запустите Python интерпретатор
python3 -c "
from app import app, db
with app.app_context():
    db.create_all()
    print('База данных инициализирована')
"

# Или создайте отдельный скрипт init_db.py
cat > init_db.py << 'EOF'
#!/usr/bin/env python3
"""
Скрипт инициализации базы данных
"""
from app import app, db
from models import Category, MenuItem, Customer, Table, Staff

def init_database():
    """Инициализация базы данных с тестовыми данными"""
    with app.app_context():
        # Создание таблиц
        db.create_all()
        
        # Проверка существующих данных
        if Category.query.count() > 0:
            print("База данных уже содержит данные")
            return
        
        # Создание категорий
        categories = [
            Category(name='Горячие блюда', description='Основные блюда'),
            Category(name='Супы', description='Первые блюда'),
            Category(name='Салаты', description='Свежие салаты'),
            Category(name='Напитки', description='Горячие и холодные напитки'),
            Category(name='Десерты', description='Сладкие блюда')
        ]
        
        for category in categories:
            db.session.add(category)
        
        db.session.commit()
        
        # Создание блюд
        menu_items = [
            MenuItem(name='Борщ украинский', price=150, category_id=2, preparation_time=15),
            MenuItem(name='Солянка сборная', price=180, category_id=2, preparation_time=20),
            MenuItem(name='Салат Цезарь', price=250, category_id=3, preparation_time=10),
            MenuItem(name='Котлета по-киевски', price=320, category_id=1, preparation_time=25),
            MenuItem(name='Кофе американо', price=80, category_id=4, preparation_time=5),
            MenuItem(name='Тирамису', price=200, category_id=5, preparation_time=10),
        ]
        
        for item in menu_items:
            db.session.add(item)
        
        # Создание столов
        tables = [
            Table(number=1, capacity=2, location='Зал'),
            Table(number=2, capacity=4, location='Зал'),
            Table(number=3, capacity=6, location='Зал'),
            Table(number=4, capacity=2, location='Терасса'),
            Table(number=5, capacity=4, location='Терасса'),
        ]
        
        for table in tables:
            db.session.add(table)
        
        db.session.commit()
        print("База данных успешно инициализирована!")

if __name__ == '__main__':
    init_database()
EOF

# Запустите скрипт инициализации
python3 init_db.py
```

### Шаг 3: Первый запуск приложения

```bash
# Запустите приложение
python3 app.py

# Или используйте Flask CLI
export FLASK_APP=app.py
export FLASK_ENV=development
flask run

# Или создайте скрипт запуска
cat > run.sh << 'EOF'
#!/bin/bash
source venv/bin/activate
export FLASK_APP=app.py
export FLASK_ENV=development
python3 app.py
EOF

chmod +x run.sh
./run.sh
```

### Шаг 4: Проверка работы

```bash
# В новом терминале проверьте доступность
curl -I http://localhost:5000

# Или используйте wget
wget --spider http://localhost:5000

# Проверьте основные эндпоинты
curl -s http://localhost:5000/ | grep -i "кафе"
curl -s http://localhost:5000/menu | grep -i "меню"
curl -s http://localhost:5000/orders | grep -i "заказы"
```

## 💾 Миграция данных

### Шаг 1: Восстановление данных из резервной копии

```bash
# Если у вас есть SQLite файл
cp cafe_system_backup.db cafe_system.db

# Если у вас есть SQL dump
sqlite3 cafe_system.db < cafe_system_dump.sql

# Если у вас есть JSON backup
python3 -c "
import sqlite3
import json

with open('database_backup.json', 'r', encoding='utf-8') as f:
    backup_data = json.load(f)

conn = sqlite3.connect('cafe_system.db')
cursor = conn.cursor()

for table_name, table_data in backup_data.items():
    if table_name.startswith('sqlite_'):
        continue
    
    columns = table_data['columns']
    data = table_data['data']
    
    # Создание таблицы если не существует
    placeholders = ', '.join(['?' for _ in columns])
    insert_query = f'INSERT OR REPLACE INTO {table_name} ({', '.join(columns)}) VALUES ({placeholders})'
    
    cursor.executemany(insert_query, data)

conn.commit()
conn.close()
print('Данные восстановлены из резервной копии')
"
```

### Шаг 2: Верификация данных

```bash
# Создайте скрипт проверки данных
cat > verify_data.py << 'EOF'
#!/usr/bin/env python3
"""
Скрипт проверки целостности данных
"""
from app import app, db
from models import Category, MenuItem, Customer, Table, Order, OrderItem, Staff, Sale

def verify_data():
    """Проверка целостности данных"""
    with app.app_context():
        print("=== Проверка данных ===")
        
        # Проверка категорий
        categories_count = Category.query.count()
        print(f"Категорий: {categories_count}")
        
        # Проверка блюд
        menu_items_count = MenuItem.query.count()
        print(f"Блюд в меню: {menu_items_count}")
        
        # Проверка клиентов
        customers_count = Customer.query.count()
        print(f"Клиентов: {customers_count}")
        
        # Проверка столов
        tables_count = Table.query.count()
        print(f"Столов: {tables_count}")
        
        # Проверка заказов
        orders_count = Order.query.count()
        print(f"Заказов: {orders_count}")
        
        # Проверка позиций заказов
        order_items_count = OrderItem.query.count()
        print(f"Позиций в заказах: {order_items_count}")
        
        # Проверка персонала
        staff_count = Staff.query.count()
        print(f"Сотрудников: {staff_count}")
        
        # Проверка продаж
        sales_count = Sale.query.count()
        print(f"Продаж: {sales_count}")
        
        print("=== Проверка связей ===")
        
        # Проверка связей между таблицами
        categories_with_items = Category.query.join(MenuItem).distinct().count()
        print(f"Категорий с блюдами: {categories_with_items}")
        
        orders_with_items = Order.query.join(OrderItem).distinct().count()
        print(f"Заказов с позициями: {orders_with_items}")
        
        print("=== Проверка завершена ===")

if __name__ == '__main__':
    verify_data()
EOF

python3 verify_data.py
```

## 🔧 Настройка для продакшена

### Шаг 1: Создание конфигурационного файла

```bash
# Создайте файл config.py
cat > config.py << 'EOF'
"""
Конфигурация приложения
"""
import os
from datetime import timedelta

class Config:
    """Базовая конфигурация"""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///cafe_system.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_RECORD_QUERIES = True
    
    # Настройки загрузки файлов
    UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER') or 'uploads'
    MAX_CONTENT_LENGTH = int(os.environ.get('MAX_CONTENT_LENGTH', 16 * 1024 * 1024))  # 16MB
    
    # Настройки сессий
    PERMANENT_SESSION_LIFETIME = timedelta(hours=2)
    
    # Настройки почты
    MAIL_SERVER = os.environ.get('MAIL_SERVER')
    MAIL_PORT = int(os.environ.get('MAIL_PORT', 587))
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'True').lower() == 'true'
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    
    # Настройки логирования
    LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')
    LOG_FILE = os.environ.get('LOG_FILE', 'app.log')

class DevelopmentConfig(Config):
    """Конфигурация для разработки"""
    DEBUG = True
    SQLALCHEMY_ECHO = True

class ProductionConfig(Config):
    """Конфигурация для продакшена"""
    DEBUG = False
    SQLALCHEMY_ECHO = False
    
    # Более строгие настройки безопасности
    FORCE_HTTPS = True
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'

class TestingConfig(Config):
    """Конфигурация для тестирования"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
EOF
```

### Шаг 2: Обновление app.py для использования конфигурации

```bash
# Создайте резервную копию
cp app.py app_backup.py

# Обновите app.py
cat > app_update.py << 'EOF'
# Добавьте в начало app.py после импортов:
import os
from config import config

# Замените строки создания приложения на:
config_name = os.environ.get('FLASK_ENV', 'development')
app = Flask(__name__)
app.config.from_object(config[config_name])
EOF

# Примените изменения вручную или используйте sed
sed -i '1i import os' app.py
sed -i '2i from config import config' app.py
```

### Шаг 3: Создание Dockerfile

```bash
# Создайте Dockerfile
cat > Dockerfile << 'EOF'
FROM python:3.11-slim

WORKDIR /app

# Установка системных зависимостей
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Копирование файлов зависимостей
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копирование исходного кода
COPY . .

# Создание директорий
RUN mkdir -p uploads logs

# Создание пользователя без root прав
RUN useradd --create-home --shell /bin/bash app_user
RUN chown -R app_user:app_user /app
USER app_user

# Открытие порта
EXPOSE 5000

# Настройка переменных окружения
ENV FLASK_APP=app.py
ENV FLASK_ENV=production
ENV PYTHONPATH=/app

# Команда запуска
CMD ["python", "app.py"]
EOF
```

### Шаг 4: Создание docker-compose.yml

```bash
# Создайте docker-compose.yml
cat > docker-compose.yml << 'EOF'
version: '3.8'

services:
  app:
    build: .
    ports:
      - "5000:5000"
    environment:
      - FLASK_ENV=production
      - SECRET_KEY=${SECRET_KEY}
      - DATABASE_URL=sqlite:///data/cafe_system.db
    volumes:
      - ./data:/app/data
      - ./uploads:/app/uploads
      - ./logs:/app/logs
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:5000/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - app
    restart: unless-stopped

volumes:
  data:
  uploads:
  logs:
EOF
```

## 🐛 Возможные проблемы и решения

### Проблема 1: Ошибки импорта

```bash
# Проверьте структуру проекта
ls -la *.py

# Проверьте синтаксис Python файлов
python3 -m py_compile app.py
python3 -m py_compile models.py

# Проверьте импорты
python3 -c "
try:
    from app import app, db
    print('Импорты app и db успешны')
except ImportError as e:
    print(f'Ошибка импорта: {e}')
"
```

### Проблема 2: Ошибки базы данных

```bash
# Проверьте существование базы данных
ls -la *.db

# Проверьте структуру базы данных
sqlite3 cafe_system.db ".tables"

# Проверьте схему таблиц
sqlite3 cafe_system.db ".schema"

# Пересоздайте базу данных
rm -f cafe_system.db
python3 init_db.py
```

### Проблема 3: Ошибки шаблонов

```bash
# Проверьте структуру templates
ls -la templates/

# Проверьте синтаксис шаблонов
python3 -c "
from jinja2 import Environment, FileSystemLoader
env = Environment(loader=FileSystemLoader('templates'))
try:
    template = env.get_template('base.html')
    print('Шаблон base.html корректен')
except Exception as e:
    print(f'Ошибка в шаблоне: {e}')
"
```

### Проблема 4: Ошибки статических файлов

```bash
# Проверьте структуру static
ls -la static/css/
ls -la static/js/

# Проверьте CSS
python3 -c "
import os
css_file = 'static/css/style.css'
if os.path.exists(css_file):
    with open(css_file) as f:
        content = f.read()
    print(f'CSS файл найден, размер: {len(content)} символов')
else:
    print('CSS файл не найден')
"
```

## ⚙️ Дополнительные настройки

### Шаг 1: Настройка логирования

```bash
# Создайте файл logging_config.py
cat > logging_config.py << 'EOF'
"""
Настройка логирования
"""
import logging
import os
from logging.handlers import RotatingFileHandler

def setup_logging(app):
    """Настройка логирования для приложения"""
    if not app.debug:
        # Создание директории для логов
        if not os.path.exists('logs'):
            os.makedirs('logs')
        
        # Настройка ротации логов
        file_handler = RotatingFileHandler(
            'logs/cafe_system.log',
            maxBytes=10240000,  # 10MB
            backupCount=10
        )
        
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
        ))
        
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)
        app.logger.setLevel(logging.INFO)
        app.logger.info('Система управления кафе запущена')
EOF
```

### Шаг 2: Создание скриптов управления

```bash
# Создайте скрипт управления manage.py
cat > manage.py << 'EOF'
#!/usr/bin/env python3
"""
Скрипт управления приложением
"""
import os
import sys
import click
from flask.cli import with_appcontext
from app import app, db
from models import Category, MenuItem, Customer, Table, Order, OrderItem, Staff, Sale

@click.group()
def cli():
    """Команды управления системой кафе"""
    pass

@cli.command()
@click.option('--sample-data', is_flag=True, help='Создать образцы данных')
def init_db(sample_data):
    """Инициализация базы данных"""
    with app.app_context():
        db.create_all()
        if sample_data:
            # Добавьте код создания образцов данных
            pass
        click.echo('База данных инициализирована')

@cli.command()
def backup_db():
    """Создание резервной копии базы данных"""
    import shutil
    import datetime
    
    timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_file = f'backup_cafe_system_{timestamp}.db'
    
    if os.path.exists('cafe_system.db'):
        shutil.copy2('cafe_system.db', backup_file)
        click.echo(f'Резервная копия создана: {backup_file}')
    else:
        click.echo('База данных не найдена')

@cli.command()
@click.argument('backup_file')
def restore_db(backup_file):
    """Восстановление базы данных из резервной копии"""
    import shutil
    
    if os.path.exists(backup_file):
        shutil.copy2(backup_file, 'cafe_system.db')
        click.echo(f'База данных восстановлена из: {backup_file}')
    else:
        click.echo('Файл резервной копии не найден')

@cli.command()
def run_tests():
    """Запуск тестов"""
    import subprocess
    result = subprocess.run(['python', '-m', 'pytest', 'tests/'], capture_output=True, text=True)
    click.echo(result.stdout)
    if result.stderr:
        click.echo(result.stderr)

if __name__ == '__main__':
    cli()
EOF

chmod +x manage.py
```

### Шаг 3: Создание системного сервиса (Linux)

```bash
# Создайте файл сервиса
sudo cat > /etc/systemd/system/cafe-management.service << 'EOF'
[Unit]
Description=Cafe Management System
After=network.target

[Service]
Type=simple
User=www-data
Group=www-data
WorkingDirectory=/path/to/cafe-management-system
Environment=FLASK_ENV=production
Environment=SECRET_KEY=your-production-secret-key
ExecStart=/path/to/cafe-management-system/venv/bin/python app.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Перезагрузите systemd
sudo systemctl daemon-reload

# Включите автозапуск
sudo systemctl enable cafe-management

# Запустите сервис
sudo systemctl start cafe-management

# Проверьте статус
sudo systemctl status cafe-management
```

## 🧪 Тестирование

### Шаг 1: Создание тестов

```bash
# Создайте директорию для тестов
mkdir -p tests

# Создайте файл conftest.py
cat > tests/conftest.py << 'EOF'
"""
Конфигурация тестов
"""
import pytest
import tempfile
import os
from app import app, db

@pytest.fixture
def client():
    """Создание тестового клиента"""
    db_fd, app.config['DATABASE'] = tempfile.mkstemp()
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
        yield client
    
    os.close(db_fd)
    os.unlink(app.config['DATABASE'])
EOF

# Создайте базовые тесты
cat > tests/test_basic.py << 'EOF'
"""
Базовые тесты приложения
"""
import pytest
from app import app, db
from models import Category, MenuItem

def test_index_page(client):
    """Тест главной страницы"""
    response = client.get('/')
    assert response.status_code == 200
    assert 'Дашборд' in response.get_data(as_text=True)

def test_menu_page(client):
    """Тест страницы меню"""
    response = client.get('/menu')
    assert response.status_code == 200

def test_add_category(client):
    """Тест добавления категории"""
    response = client.post('/categories/add', data={
        'name': 'Тестовая категория',
        'description': 'Описание тестовой категории'
    })
    assert response.status_code == 302  # Redirect after successful creation

def test_database_models():
    """Тест моделей базы данных"""
    with app.app_context():
        db.create_all()
        
        # Создание категории
        category = Category(name='Тест', description='Тестовая категория')
        db.session.add(category)
        db.session.commit()
        
        # Проверка создания
        assert Category.query.count() == 1
        assert Category.query.first().name == 'Тест'
        
        db.session.delete(category)
        db.session.commit()
EOF

# Установите pytest
pip install pytest pytest-flask

# Запустите тесты
python -m pytest tests/ -v
```

### Шаг 2: Создание скрипта полной проверки

```bash
# Создайте скрипт полной проверки
cat > full_check.py << 'EOF'
#!/usr/bin/env python3
"""
Полная проверка системы после переноса
"""
import os
import sys
import requests
import time
import subprocess
from urllib.parse import urljoin

def check_files():
    """Проверка наличия всех необходимых файлов"""
    required_files = [
        'app.py',
        'models.py',
        'requirements.txt',
        'README.md',
        'templates/base.html',
        'templates/index.html',
        'static/css/style.css',
        'static/js/script.js'
    ]
    
    print("=== Проверка файлов ===")
    missing_files = []
    
    for file in required_files:
        if os.path.exists(file):
            print(f"✓ {file}")
        else:
            print(f"✗ {file} - ОТСУТСТВУЕТ")
            missing_files.append(file)
    
    if missing_files:
        print(f"\nОтсутствуют файлы: {', '.join(missing_files)}")
        return False
    
    print("Все файлы найдены")
    return True

def check_dependencies():
    """Проверка установленных зависимостей"""
    print("\n=== Проверка зависимостей ===")
    try:
        import flask
        print(f"✓ Flask: {flask.__version__}")
    except ImportError:
        print("✗ Flask не установлен")
        return False
    
    try:
        import flask_sqlalchemy
        print(f"✓ Flask-SQLAlchemy: {flask_sqlalchemy.__version__}")
    except ImportError:
        print("✗ Flask-SQLAlchemy не установлен")
        return False
    
    return True

def check_database():
    """Проверка базы данных"""
    print("\n=== Проверка базы данных ===")
    try:
        from app import app, db
        from models import Category, MenuItem
        
        with app.app_context():
            # Проверка подключения
            db.engine.execute('SELECT 1')
            print("✓ Подключение к базе данных")
            
            # Проверка таблиц
            categories_count = Category.query.count()
            items_count = MenuItem.query.count()
            
            print(f"✓ Категорий: {categories_count}")
            print(f"✓ Блюд: {items_count}")
            
            return True
    except Exception as e:
        print(f"✗ Ошибка базы данных: {e}")
        return False

def check_web_server():
    """Проверка веб-сервера"""
    print("\n=== Проверка веб-сервера ===")
    base_url = 'http://localhost:5000'
    
    # Запуск сервера в фоне
    server_process = subprocess.Popen([
        sys.executable, 'app.py'
    ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    
    # Ждем запуска сервера
    time.sleep(3)
    
    try:
        # Проверка основных страниц
        pages = ['/', '/menu', '/orders', '/customers', '/tables']
        
        for page in pages:
            url = urljoin(base_url, page)
            response = requests.get(url, timeout=5)
            
            if response.status_code == 200:
                print(f"✓ {page} - OK")
            else:
                print(f"✗ {page} - Статус {response.status_code}")
        
        server_process.terminate()
        return True
        
    except requests.exceptions.RequestException as e:
        print(f"✗ Ошибка подключения к серверу: {e}")
        server_process.terminate()
        return False

def main():
    """Основная функция проверки"""
    print("🔍 Полная проверка системы управления кафе")
    print("=" * 50)
    
    checks = [
        check_files,
        check_dependencies,
        check_database,
        check_web_server
    ]
    
    passed = 0
    total = len(checks)
    
    for check in checks:
        if check():
            passed += 1
    
    print(f"\n📊 Результат: {passed}/{total} проверок пройдено")
    
    if passed == total:
        print("🎉 Все проверки пройдены успешно!")
        print("Система готова к работе!")
    else:
        print("⚠️  Обнаружены проблемы, требующие решения")
        sys.exit(1)

if __name__ == '__main__':
    main()
EOF

chmod +x full_check.py
```

## 📋 Финальный чек-лист

### Перед коммитом:

- [ ] Все файлы скопированы
- [ ] Виртуальное окружение создано
- [ ] Зависимости установлены
- [ ] База данных инициализирована
- [ ] Приложение запускается
- [ ] Основные страницы открываются
- [ ] Тесты проходят
- [ ] .gitignore настроен
- [ ] Переменные окружения настроены

### Коммит и пуш:

```bash
# Добавьте все файлы в Git
git add .

# Сделайте коммит
git commit -m "Инициальная версия системы управления кафе

- Добавлены модели данных для кафе
- Реализован веб-интерфейс с Bootstrap
- Добавлены функции управления меню, заказами, столами
- Настроена база данных SQLite
- Добавлена документация и инструкции по установке"

# Отправьте в удаленный репозиторий
git push origin main

# Создайте тег версии
git tag -a v1.0.0 -m "Первая версия системы управления кафе"
git push origin v1.0.0
```

## 📞 Поддержка

Если у вас возникли проблемы:

1. **Проверьте логи:**
   ```bash
   tail -f logs/cafe_system.log
   ```

2. **Запустите проверку:**
   ```bash
   python3 full_check.py
   ```

3. **Проверьте статус сервиса:**
   ```bash
   sudo systemctl status cafe-management
   ```

4. **Откройте issue в репозитории** с подробным описанием проблемы

---

✅ **Поздравляем! Система управления кафе успешно перенесена в новый репозиторий!**