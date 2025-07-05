#!/usr/bin/env python3
"""
Простой скрипт запуска системы управления кафе
"""
import os
import sys
import subprocess
import importlib.util

def check_python_version():
    """Проверка версии Python"""
    if sys.version_info < (3, 8):
        print("❌ Требуется Python 3.8 или выше")
        print(f"   Текущая версия: {sys.version}")
        sys.exit(1)
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor}")

def check_dependencies():
    """Проверка зависимостей"""
    dependencies = ['flask', 'flask_sqlalchemy', 'werkzeug']
    missing = []
    
    for dep in dependencies:
        if importlib.util.find_spec(dep) is None:
            missing.append(dep)
    
    if missing:
        print(f"❌ Отсутствуют зависимости: {', '.join(missing)}")
        print("   Установите их командой: pip install -r requirements.txt")
        return False
    
    print("✅ Все зависимости установлены")
    return True

def install_dependencies():
    """Установка зависимостей"""
    try:
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'])
        print("✅ Зависимости успешно установлены")
        return True
    except subprocess.CalledProcessError:
        print("❌ Ошибка при установке зависимостей")
        return False

def check_port():
    """Проверка доступности порта"""
    import socket
    
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)
        result = sock.connect_ex(('localhost', 5000))
        sock.close()
        
        if result == 0:
            print("⚠️  Порт 5000 занят. Система может не запуститься.")
            return False
        else:
            print("✅ Порт 5000 свободен")
            return True
    except:
        print("✅ Порт 5000 доступен")
        return True

def main():
    """Основная функция запуска"""
    print("🍽️  ЗАПУСК ПРОСТОЙ СИСТЕМЫ УПРАВЛЕНИЯ КАФЕ")
    print("=" * 50)
    
    # Проверка Python
    check_python_version()
    
    # Проверка зависимостей
    if not check_dependencies():
        print("\n🔧 Попытка установки зависимостей...")
        if not install_dependencies():
            sys.exit(1)
    
    # Проверка порта
    check_port()
    
    # Проверка файла приложения
    if not os.path.exists('simple_app.py'):
        print("❌ Файл simple_app.py не найден")
        sys.exit(1)
    
    print("\n✅ Все проверки пройдены!")
    print("🚀 Запуск системы...")
    print("=" * 50)
    
    # Запуск приложения
    try:
        subprocess.run([sys.executable, 'simple_app.py'])
    except KeyboardInterrupt:
        print("\n\n👋 Система остановлена пользователем")
    except Exception as e:
        print(f"\n❌ Ошибка при запуске: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()