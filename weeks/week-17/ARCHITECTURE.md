# Архитектура shipments-s13

`shipments-s13` - финальный проект для варианта `332/s13`. Система управляет отправлениями (`shipments`) и хранит дополнительное поле варианта `tracking`.

## Сервисы

| Сервис     | Назначение                      | Порт | Протоколы |
| ---       | ---                              | ---: | --- |
| `gateway` | Внешняя точка входа для клиентов | 8080 | REST `/api/shipments`, GraphQL `/graphql` |
| `shipments-svc-s13` | Владелец данных отправлений и gRPC-контракта `ShipmentsService` | 8130, 8131 | REST health/admin, gRPC `shipments.v1` |
| `audit-service` | Асинхронный журнал событий по отправлениям | 8132 | REST `/internal/events` |

## Взаимодействие

```text
Client
  |
  | REST /api/shipments or GraphQL /graphql
  v
gateway
  |
  | gRPC shipments.v1.ShipmentsService
  v
shipments-svc-s13
  |
  | best-effort REST event: shipment.created, shipment.status_updated
  v
audit-service
```

Gateway не хранит состояние и может масштабироваться горизонтально. `shipments-svc-s13` владеет базой отправлений и публикует событие в audit-service после успешной записи. Если audit-service временно недоступен, создание shipment не ломается: ошибка доставки события логируется, а основной сценарий остается успешным.

## Данные

- `shipments-svc-s13`: SQLite `/data/shipments.db`, таблица `shipments`.
- `audit-service`: SQLite `/data/audit.db`, таблица `audit_events`.
- Общей базы данных нет: каждый сервис владеет только своими данными.
- Для Docker Compose и Kubernetes данные вынесены в volume/PVC.

## API

Внешний REST:

- `GET /api/shipments`
- `POST /api/shipments`
- `GET /api/shipments/{id}`
- `PATCH /api/shipments/{id}/status`

GraphQL:

- Type: `Shipment`
- Query: `shipments`
- Mutation: `createShipment`

gRPC:

- Package: `shipments.v1`
- Service: `ShipmentsService`
- Proto: `proto/shipments/v1/shipments.proto`
- Методы: `CreateShipment`, `GetShipment`, `ListShipments`, `UpdateShipmentStatus`, `StreamShipmentEvents`.

## Инфраструктура

- Dockerfile есть для каждого сервиса.
- `docker-compose.yml` запускает всю систему одной командой.
- Kubernetes-манифесты лежат в `k8s/`; основное приложение использует имена из варианта: `shipments-app`, `shipments-container`, `shipments-svc-s13`.
- Helm chart лежит в `chart/` и имеет overrides для dev/prod.
- CI описан в `.github/workflows/week17.yml`: установка зависимостей с pip cache, compile/lint, `make test WEEK=17`, сборка трех Docker-образов и публикация артефактов.

## Наблюдаемость и надежность

- У всех сервисов есть `/health`.
- В Compose и Kubernetes настроены healthchecks/readiness/liveness probes.
- Сервисы пишут базовые логи в stdout.
- Контейнеры в Kubernetes имеют requests/limits.
- Внешний трафик идет через gateway; внутренний gRPC-порт `8131` не требуется публиковать наружу в production.
