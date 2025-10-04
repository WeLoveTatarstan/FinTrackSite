#!/usr/bin/env python
"""
Скрипт для проверки Django проекта и применения миграций
"""
import os
import sys
import django
from pathlib import Path

# Добавляем путь к проекту
project_path = Path(__file__).parent
sys.path.insert(0, str(project_path))

# Настраиваем Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'FinTrack.settings')
django.setup()

from django.core.management import execute_from_command_line

if __name__ == '__main__':
    print("Проверка Django проекта...")
    
    # Проверяем проект
    try:
        execute_from_command_line(['manage.py', 'check'])
        print("✅ Django проект прошел проверку!")
    except Exception as e:
        print(f"❌ Ошибка при проверке: {e}")
    
    # Применяем миграции
    try:
        execute_from_command_line(['manage.py', 'migrate'])
        print("✅ Миграции применены успешно!")
    except Exception as e:
        print(f"❌ Ошибка при применении миграций: {e}")
    
    print("Готово!")
