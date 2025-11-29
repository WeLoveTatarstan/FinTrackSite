# Используем официальный Python образ
FROM python:3.11-slim

# Устанавливаем рабочую директорию
WORKDIR /app

# Устанавливаем системные зависимости
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Копируем файл зависимостей
COPY requirements.txt .

# Устанавливаем Python зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Копируем весь проект
COPY . .

# Создаем директории для медиа и статических файлов
RUN mkdir -p /app/media /app/staticfiles

# Открываем порт
EXPOSE 8000

# Команда для запуска приложения (будет переопределена в docker-compose.yml)
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]

