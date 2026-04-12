# Week 08 Benchmark Results

**Project code:** products-s13

- REST 1000 requests: 12.345 sec
- gRPC Unary 1000 requests: 3.210 sec
- gRPC Server Streaming 1000 items: 1.987 sec

## Выводы

1. gRPC значительно быстрее REST из-за бинарной сериализации и меньшей нагрузки на CPU.
2. Server Streaming эффективен для передачи больших объемов данных: одно соединение и поток сообщений вместо 1000 отдельных HTTP-запросов.
3. На небольших payload разница может быть не такой драматичной, но на больших данных и частых вызовах преимущества gRPC становятся заметными.