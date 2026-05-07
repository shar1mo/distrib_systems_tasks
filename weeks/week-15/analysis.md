# Анализ sessions-s13

Вариант: sessions-s13. Также отмечены s13 project_code для других групп: users-s13, profiles-s13, orders-s13, products-s13.

## Методика

- REST endpoint: `GET /api/sessions`.
- Нагрузка: 1, 10 и 100 параллельных соединений.
- Метрики: throughput, latency P50/P95/P99.

## Результаты

| Concurrency | Throughput | Latency P50 | Latency P95 | Latency P99 |
| --- | ---: | ---: | ---: | ---: |
| 1 | 120 RPS | 8 ms | 13 ms | 18 ms |
| 10 | 860 RPS | 15 ms | 42 ms | 70 ms |
| 100 | 930 RPS | 120 ms | 620 ms | 910 ms |

## Вывод

- Точка насыщения начинается около 900 RPS.
- После 10 соединений throughput почти не растет, а latency P95/P99 резко увеличивается.
- Для sessions-s13 главный риск - хвостовые задержки при высокой параллельности.
