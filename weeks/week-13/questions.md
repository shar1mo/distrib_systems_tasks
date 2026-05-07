# Вопросы для самопроверки

- Helm шаблонизирует Kubernetes YAML и убирает копипасту.
- `--set` имеет больший приоритет, чем `values.yaml`.
- `include` и `_helpers.tpl` нужны для переиспользуемых шаблонных функций.
- Отступы важны из-за YAML; `indent`/`nindent` выравнивают вставки.
- Откат: `helm rollback <release> <revision>`.
- Да, через `helm template`.
