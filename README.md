# -8- · n8n Workflows Portfolio

Коллекция n8n-воркфлоу для портфолио.

---

## 📡 Brand Monitoring — Telegram → OpenAI → Google Sheets / Notion

**Файл:** [`n8n_workflow_brand_monitoring.json`](n8n_workflow_brand_monitoring.json)

### Сценарий

Мониторинг упоминаний бренда **ChatGPT** в Telegram-группе → анализ тональности и суммаризация через OpenAI (GPT-4o-mini) → сохранение результата в **Google Sheets** и **Notion** параллельно.

### Архитектура (7 нод)

```
Telegram Trigger
      │
      ▼
Filter Brand Mentions  (Code — regex /chatgpt/i)
      │
      ▼
OpenAI Sentiment Analysis  (GPT-4o-mini, JSON output)
      │
      ▼
Parse AI Response  (Code — merge original + AI data)
      │
      ├──▶ Google Sheets — Save
      │
      ├──▶ Notion — Save
      │
      ▼
    Done
```

### Что делает каждый узел

| # | Узел | Тип | Описание |
|---|------|-----|----------|
| 1 | **Telegram Trigger** | `telegramTrigger` | Слушает все сообщения в группе (webhook) |
| 2 | **Filter Brand Mentions** | `code` | Фильтрует: пропускает только сообщения с «ChatGPT» (регистронезависимо). Извлекает метаданные: автор, чат, дата |
| 3 | **OpenAI Sentiment Analysis** | `openAi` | Отправляет текст в GPT-4o-mini с system-промптом для анализа тональности. Возвращает JSON: `sentiment`, `confidence`, `summary`, `topics` |
| 4 | **Parse AI Response** | `code` | Парсит JSON-ответ OpenAI, объединяет с исходными данными. Обрабатывает edge-case: markdown-блоки в ответе, невалидный JSON |
| 5 | **Google Sheets — Save** | `googleSheets` | Добавляет строку в таблицу (10 колонок: date, chat, user, message, sentiment, confidence, summary, topics, message_id, chat_id) |
| 6 | **Notion — Save** | `notion` | Создаёт страницу в Notion-базе (8 полей: Date, Chat, User, Message, Sentiment, Confidence, Summary, Topics) |
| 7 | **Done** | `set` | Финальный узел — подтверждение сохранения |

### Пример данных в Google Sheets

| date | chat | user | message | sentiment | confidence | summary | topics |
|------|------|------|---------|-----------|------------|---------|--------|
| 2026-04-03T12:00:00Z | AI Talk | @ivan | ChatGPT стал намного быстрее после обновления! | positive | 0.92 | Пользователь отмечает улучшение скорости ChatGPT после обновления | обновление, производительность |
| 2026-04-03T14:30:00Z | AI Talk | @maria | ChatGPT опять глючит, не отвечает нормально | negative | 0.88 | Жалоба на нестабильную работу ChatGPT | баг, стабильность |

### Как использовать

1. **Импортируйте** `n8n_workflow_brand_monitoring.json` в n8n (Settings → Import workflow)
2. **Настройте credentials:**
   - **Telegram Bot** — создайте бота через [@BotFather](https://t.me/BotFather), добавьте его в группу
   - **OpenAI API** — ключ из [platform.openai.com](https://platform.openai.com)
   - **Google Sheets** — OAuth2 или Service Account
   - **Notion** — Internal Integration из [notion.so/my-integrations](https://www.notion.so/my-integrations)
3. **Замените placeholder-значения** в JSON:
   - `GOOGLE_SHEET_ID` — ID вашей Google-таблицы
   - `NOTION_DATABASE_ID` — ID Notion-базы данных
4. **Подготовьте Google Sheets** — создайте таблицу с колонками: `date`, `chat`, `user`, `message`, `sentiment`, `confidence`, `summary`, `topics`, `message_id`, `chat_id`
5. **Подготовьте Notion** — создайте базу данных с полями: Date (date), Chat (rich text), User (rich text), Message (title), Sentiment (select: positive/negative/neutral), Confidence (number), Summary (rich text), Topics (rich text)
6. **Активируйте** воркфлоу

### Кастомизация

- **Изменить бренд для мониторинга:** откройте узел «Filter Brand Mentions» и замените `chatgpt` в regex на нужное ключевое слово
- **Использовать только Google Sheets или только Notion:** удалите ненужную ветку в connections
- **Добавить уведомления:** подключите Telegram sendMessage или Slack после узла «Done» для алертов о негативных упоминаниях
- **Изменить модель OpenAI:** замените `gpt-4o-mini` на `gpt-4o` или другую модель в узле «OpenAI Sentiment Analysis»
