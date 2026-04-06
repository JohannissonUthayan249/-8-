# -8-
н8н

## RAG Demo — Конная амуниция (Horse Equipment)

Файл: `n8n_workflow_rag_horse_equipment.json`

### Описание

Демонстрационный n8n-воркфлоу, реализующий RAG (Retrieval-Augmented Generation) на тему **конной амуниции и снаряжения для лошадей**.

### Архитектура

Воркфлоу состоит из **двух потоков** (15 нодов):

#### Поток 1 — Заполнение базы знаний (запустить один раз)
```
Seed Knowledge Base → Embed Documents (OpenAI) → Qdrant Insert Documents
```
Генерирует 10 чанков с экспертной информацией о конной амуниции и загружает их в векторную базу Qdrant.

#### Поток 2 — Обработка вопросов (основной)
```
Telegram Trigger → Parse Input → IF Welcome
  ├─ true  → Welcome Reply (приветствие)
  └─ false → Embed Query → Qdrant Retrieve → Build RAG Context
             → Generate Answer (GPT-4o) → Send Answer to Telegram
             → Prepare Log Entry → Log to Google Sheets
             (ошибки → Error Reply)
```

### Категории знаний

| Категория | Темы |
|-----------|------|
| 🐎 Сёдла | Виды сёдел, подбор размера, подпруги, вальтрапы |
| ⛓️ Оголовья | Уздечки, трензеля, хакаморы, размеры оголовий |
| 🧣 Попоны | Зимние, дождевые, денниковые, антимоскитные |
| 🦵 Защита ног | Ногавки, бинты, колокольчики |
| 👢 Всадник | Шлемы, сапоги, бриджи, перчатки |
| 🔧 Уход | Уход за кожаной амуницией |

### Необходимые учётные данные

| Сервис | Credential в n8n |
|--------|-----------------|
| Telegram Bot | `telegramApi` |
| OpenAI API | `openAiApi` |
| Qdrant | `qdrantApi` |
| Google Sheets | `googleSheetsOAuth2Api` |

### Как запустить

1. Импортируйте `n8n_workflow_rag_horse_equipment.json` в n8n
2. Настройте учётные данные (Telegram Bot Token, OpenAI API Key, Qdrant URL, Google Sheets)
3. Запустите нод **Seed Knowledge Base** вручную для заполнения базы знаний
4. Активируйте воркфлоу — бот готов к работе!

### Технологии

- **Embedding**: OpenAI `text-embedding-3-small`
- **Vector Store**: Qdrant (коллекция `horse_equipment`)
- **LLM**: GPT-4o (temperature=0.3)
- **Интерфейс**: Telegram Bot
- **Логирование**: Google Sheets
