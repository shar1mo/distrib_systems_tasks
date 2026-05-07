# Audit notifications-s13

Вариант: notifications-s13. Также отмечены s13 project_code для других групп: items-s13, devices-s13, sessions-s13.

## Проверки

- Broken Access Control - нужен middleware авторизации для операций с чужими notifications.
- Injection - входное поле channel валидировать whitelist-ом: email, sms, push.
- Secrets - ключи БД и JWT хранить только в CI/CD secrets или Kubernetes Secret.
- Security Misconfiguration - выключить debug, закрыть лишние порты, включить resource limits.
- Logging - не писать токены, cookies и персональные данные в application logs.
- Transport Security - внешний доступ только через HTTPS.

## Рекомендации

- Добавить проверку владельца ресурса на сервере.
- Валидировать body и query параметры схемой.
- Ограничить права сервисного аккаунта принципом least privilege.
- Подключить SAST/dependency scan в CI.
