# -8-
н8н

## Архитектура workflow

```
Telegram Trigger → Code Router → Route Switch
                                   ├─ Output 0 (start)    → Telegram API1 (sendPhoto — приветствие с фото)
                                   ├─ Output 1 (select)   → Code in JavaScript → HTTP Request → Code in JavaScript1 → Telegram API
                                   ├─ Output 2 (category) → Category Code → Airtable Lookup → Category Format → Category Reply
                                   └─ Output 3 (fallback) → OpenAI Response → Build AI Reply → Telegram AI Reply
```

### Нода Route Switch — настройка

Нода `Route Switch` (тип `n8n-nodes-base.switch`, v3) заменяет цепочку `If` + `IF AI` и имеет **4 выхода**:

| Выход | Условие | Куда идёт |
|-------|---------|-----------|
| 0 — `start` | `action` == `/start` | **Telegram API1** — отправляет приветственное фото |
| 1 — `select` | `action` == `подобрать` | **Code in JavaScript** → подбор ароматов |
| 2 — `category` | `action` starts with `category:` | **Category Code** → Airtable Lookup → каталог |
| 3 — fallback | всё остальное | **OpenAI Response** → AI-ответ |

### Что было исправлено

**Проблема:** при `/start` вместо приветственного фото приходили картинки ароматов из Airtable.

**Причина:** ноды `If` + `IF AI` неправильно маршрутизировали `/start` — команда попадала в ветку Airtable вместо welcome-ветки.

**Решение:** заменили `If` + `IF AI` на одну ноду `Route Switch` с явными условиями для каждого типа действия. Теперь `/start` гарантированно идёт на Output 0 → `Telegram API1` (sendPhoto).

### Перед импортом

В файле `n8n_workflow.json` замените плейсхолдеры:

- `YOUR_WELCOME_PHOTO_URL` — URL приветственного фото
- `YOUR_BASE_ID` — ID базы Airtable
- `YOUR_TABLE_NAME` — имя таблицы Airtable
- Credential ID (`telegram-cred`, `airtable-cred`, `openai-cred`) — свяжите со своими credentials в n8n
