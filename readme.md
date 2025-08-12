# Сборка проекта (Docker)

## Сборка для хоста
1. Для первого разворота выполните файл first_install.sh
2. Для последующих сборок можно ограничиться файлом install.py

## Ручная локальная сборка
1. Создание Docker сети: docker network create --gateway 172.22.0.1 --subnet 172.22.0.0/16 autod_aster_3
2. Сборка проекта: docker-compose build
3. Запуск проекта: docker-compose up -d