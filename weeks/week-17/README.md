# Финальный проект: shipments-s13

Мини-система из трех сервисов для управления отправлениями. Вариант: группа `332`, студент `s13`, ресурс `shipments`, дополнительное поле `tracking`.

## Быстрый запуск

```bash
cd weeks/week-17
docker compose up --build
```

После запуска gateway доступен на `http://localhost:8080`.

## Проверка REST

```bash
curl http://localhost:8080/health

curl -X POST http://localhost:8080/api/shipments \
  -H "Content-Type: application/json" \
  -d '{"destination":"Novosibirsk","tracking":"S13-TRACK-001"}'

curl http://localhost:8080/api/shipments
```

Обновление статуса:

```bash
curl -X PATCH http://localhost:8080/api/shipments/1/status \
  -H "Content-Type: application/json" \
  -d '{"status":"in_transit"}'
```

## Проверка GraphQL

Endpoint: `http://localhost:8080/graphql`.

```graphql
mutation {
  createShipment(destination: "Tomsk", tracking: "S13-TRACK-002") {
    id
    destination
    tracking
    status
  }
}
```

```graphql
query {
  shipments {
    id
    destination
    tracking
    status
    createdAt
  }
}
```

## Структура

- `services/gateway` - внешний REST и GraphQL gateway.
- `services/shipments_service` - основной сервис `shipments-svc-s13`, REST health/admin и gRPC `ShipmentsService`.
- `services/audit_service` - журнал событий отправлений.
- `proto/shipments/v1/shipments.proto` - gRPC-контракт.
- `generated/` - сгенерированные Python stubs для gRPC.
- `k8s/` - Kubernetes-манифесты.
- `chart/` - Helm chart.

## Локальная разработка без Docker

```bash
cd weeks/week-17
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
make proto
```

Запуск сервисов вручную требует трех терминалов и переменных `PYTHONPATH`:

```bash
PYTHONPATH=services/audit_service DATABASE_PATH=/tmp/audit.db uvicorn app.main:app --host 0.0.0.0 --port 8132
PYTHONPATH=services/shipments_service:generated DATABASE_PATH=/tmp/shipments.db AUDIT_URL=http://localhost:8132 uvicorn app.main:app --host 0.0.0.0 --port 8130
PYTHONPATH=services/gateway:generated SHIPMENTS_GRPC_TARGET=localhost:8131 uvicorn app.main:app --host 0.0.0.0 --port 8080
```

## Kubernetes и Helm

```bash
kubectl apply -f k8s/
kubectl port-forward svc/gateway-service 8080:8080
```

Helm:

```bash
helm upgrade --install shipments-s13 ./chart -f chart/values-dev.yaml
```

## Тест курса

Из корня репозитория:

```bash
GROUP=332 STUDENT_ID=s13 make test WEEK=17
```
