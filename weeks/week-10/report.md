# Отчет по Docker

## Размер образа
Размер образа (size): указать после команды docker images

## Layers (слои)
В Docker каждый шаг Dockerfile создает отдельный layer (слой).

В данном проекте слои создаются следующими командами:
- FROM python:3.11-slim
- COPY requirements.txt .
- RUN pip install -r requirements.txt
- COPY . .
- COPY --from=builder /install /usr/local

Посмотреть layers можно командой:
docker history week10-app

## Количество слоев
Количество layer: указать после docker history

## Команды

### Сборка
docker build -t week10-app .

### Запуск
docker run -p 8267:8267 week10-app