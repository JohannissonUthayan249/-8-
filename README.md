# -8-
n8n Telegram Bot Workflow

## Описание
n8n воркфлоу для Telegram-бота с функциями подбора и AI-ответов.

### Маршрутизация
- **Telegram Trigger** → **Code Router** → **If** (проверка `action == "подобрать"`)
  - ✅ True: Code in JavaScript → HTTP Request → Code in JavaScript1 → Telegram API
  - ❌ False: **IF AI** (проверка `action != "/start"`)
    - ✅ True: OpenAI Response → Build AI Reply → Telegram AI Reply
    - ❌ False: Telegram API1 (приветственное сообщение /start)

### Исправленная ошибка
**Проблема:** При нажатии на `/start` приходило сообщение с кнопки "подобрать".

**Причина:** В узле **Code Router** не различались команда `/start` (текстовое сообщение) и нажатие кнопки "подобрать" (callback_query). Действие из callback_query и текстовой команды обрабатывались одинаково, что приводило к неправильной маршрутизации.

**Решение:** Узел **Code Router** теперь корректно разделяет:
1. `callback_query.data` — для обработки нажатий inline-кнопок (например, "подобрать")
2. `message.text` — для обработки текстовых команд (например, "/start")

Узел **If** проверяет `action == "подобрать"` (строгое сравнение), что гарантирует, что только callback с данными "подобрать" попадает в ветку подбора.
