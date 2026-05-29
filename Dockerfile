# Берём за основу официальный образ Python
FROM python:3.11-slim

# Устанавливаем рабочую директорию внутри контейнера
WORKDIR /app

# Копируем файл с зависимостями внутрь контейнера
COPY requirements.txt .

# Устанавливаем зависимости Python
RUN pip install --no-cache-dir -r requirements.txt

# Копируем весь наш проект внутрь контейнера
COPY . .

# Открываем порт, который слушает Flask
EXPOSE 5000

# Команда для запуска бота
CMD ["python", "app.py"]
