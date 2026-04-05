# -8-
н8н

---

## Мониторинг тикетов и чата на негатив

**Файл:** `n8n_workflow_ticket_negativity_monitor.json`

Бот следит за входящими сообщениями в Zendesk и Intercom. Если клиент пишет слова-триггеры — немедленно уведомляет менеджера и повышает приоритет тикета.

### Слова-триггеры

| Слово | Категория |
|---|---|
| отмена | Отказ от услуги |
| возврат | Финансовая претензия |
| ужасно | Негативная оценка |
| юрист | Юридическая угроза |
| мошенники | Обвинение |
| судиться | Юридическая угроза |

### Архитектура воркфлоу (11 нод)

```
Zendesk Trigger ──┐
                   ├→ Normalize Message → Check Trigger Words → Is Negative?
Intercom Trigger ──┘                                              │
                                                        ┌────────YES────────┐
                                                        │                    │
                                                   Format Alert         No Action
                                                        │
                                          ┌─────────────┼─────────────┐
                                          │             │             │
                                   Notify Manager  Zendesk Escalate  Intercom Escalate
                                   (Telegram)      (set Urgent)     (add tag)
                                                        │             │
                                                        └──────┬──────┘
                                                               │
                                                       Log to Google Sheets
```

### Описание нод

| # | Нода | Тип | Описание |
|---|------|-----|----------|
| 1 | Zendesk Trigger | zendeskTrigger | Срабатывает при новом/обновлённом тикете |
| 2 | Intercom Trigger | intercomTrigger | Срабатывает при новом сообщении |
| 3 | Normalize Message | Code | Приводит данные из обоих источников к единому формату |
| 4 | Check Trigger Words | Code | Проверяет текст на слова-триггеры (regex) |
| 5 | Is Negative? | IF | Разделяет поток: негатив / нет негатива |
| 6 | Format Alert | Code | Формирует текст уведомления для менеджера |
| 7 | Notify Manager (Telegram) | Telegram | Отправляет 🚨 уведомление менеджеру |
| 8 | Zendesk — Escalate Priority | HTTP Request | Повышает приоритет тикета до Urgent |
| 9 | Intercom — Tag & Escalate | HTTP Request | Добавляет тег эскалации в разговор |
| 10 | Log to Google Sheets | Google Sheets | Логирует инцидент в таблицу |
| 11 | No Action | NoOp | Пропуск при отсутствии негатива |

### Настройка

1. **Импорт:** Импортируйте `n8n_workflow_ticket_negativity_monitor.json` в n8n
2. **Credentials:** Настройте учётные данные:
   - **Zendesk** — Basic Auth (email/token + `/token` суффикс)
   - **Intercom** — HTTP Header Auth (`Authorization: Bearer <token>`)
   - **Telegram Bot** — Bot token
   - **Google Sheets** — OAuth2
3. **Переменные окружения n8n:**
   - `MANAGER_TELEGRAM_CHAT_ID` — Chat ID менеджера в Telegram
   - `ZENDESK_SUBDOMAIN` — поддомен Zendesk (например `mycompany`)
   - `INTERCOM_ESCALATION_TAG_ID` — ID тега эскалации в Intercom
4. **Google Sheets:** Создайте таблицу с колонками: `timestamp`, `ticketId`, `source`, `customerName`, `triggeredWords`, `message`
5. **Активируйте** воркфлоу в n8n

### Расширение слов-триггеров

Чтобы добавить новые слова-триггеры, откройте ноду **Check Trigger Words** и добавьте слова в массив `triggerWords`:

```javascript
const triggerWords = [
  'отмена',
  'возврат',
  'ужасно',
  'юрист',
  'мошенники',
  'судиться',
  // Добавьте новые слова сюда:
  'жалоба',
  'обман'
];
```
