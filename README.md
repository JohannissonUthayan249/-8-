# -8-
n8n Telegram Bot Workflow — Парфюмерный гид

## Описание

n8n воркфлоу для Telegram-бота — парфюмерного гида с каталогом ароматов, AI-подбором через OpenAI GPT-4o и интеграцией с Airtable.

### Функции бота

| Команда / кнопка | Что делает |
|-----------------|------------|
| `/start` | Приветствие с фото + главное меню (inline-кнопки) |
| 📖 Каталог ароматов | Показывает категории: цветочные, древесные, восточные, цитрусовые |
| ✨ Подобрать | AI-консультант помогает выбрать аромат |
| 🎓 Инфо | Краткая справка о возможностях бота |
| ⬅️ Назад | Возврат в главное меню |
| Категория (🌸/🌲/🌙/🍋) | Поиск ароматов по категории в Airtable |
| Произвольный текст | AI-ответ от GPT-4o |

---

## Архитектура воркфлоу

```
Telegram Trigger → Code Router → Route Switch
                                   ├─ telegram → Telegram Send (sendMessage / sendPhoto)
                                   ├─ ai       → OpenAI Request → Build AI Reply → Telegram AI Reply
                                   └─ airtable → Airtable Lookup (placeholder)
```

### Узлы (8 шт.)

| # | Узел | Тип | Назначение |
|---|------|-----|------------|
| 1 | Telegram Trigger | telegramTrigger | Получает message + callback_query |
| 2 | Code Router | code | Вся логика маршрутизации в одном узле |
| 3 | Route Switch | switch | Роутит по `routeType`: telegram / ai / airtable |
| 4 | Telegram Send | httpRequest | Отправляет сообщения/фото через Telegram API |
| 5 | OpenAI Request | httpRequest | Запрос к GPT-4o |
| 6 | Build AI Reply | code | Формирует ответ из OpenAI response |
| 7 | Telegram AI Reply | httpRequest | Отправляет AI-ответ пользователю |
| 8 | Airtable Lookup | code | Placeholder для поиска по Airtable |

---

## Code Router — логика маршрутизации

Code Router — центральный узел. Он определяет тип входящего сообщения и формирует структурированный output:

### Выходные поля

| Поле | Тип | Описание |
|------|-----|----------|
| `chatId` | number | ID чата Telegram |
| `userId` | number | ID пользователя |
| `messageId` | number | ID сообщения |
| `callbackQueryId` | string | ID callback_query (для inline-кнопок) |
| `originalText` | string | Текст сообщения или callback_data |
| `shouldCallAi` | boolean | Нужно ли вызывать OpenAI |
| `telegramMethod` | string | Метод Telegram API: sendMessage / sendPhoto |
| `telegramPayload` | object | Готовый payload для Telegram API |
| `aiPrompt` | string | Системный промпт для OpenAI |
| `routeType` | string | Маршрут: `telegram` / `ai` / `airtable` |
| `categoryKey` | string | Ключ категории для Airtable |
| `airtableFormula` | string | Формула для поиска в Airtable |

### Таблица маршрутизации

| Вход | routeType | Действие |
|------|-----------|----------|
| `/start` (message) | telegram | sendPhoto с приветствием + mainKeyboard |
| `catalog` (callback) | telegram | sendMessage с catalogKeyboard |
| `pick` (callback) | ai | AI-промпт для подбора аромата |
| `info` (callback) | telegram | sendMessage со справкой |
| `back` (callback) | telegram | sendPhoto с mainKeyboard (возврат) |
| `category:*` (callback) | airtable | Поиск по категории в Airtable |
| Произвольный текст | ai | AI-промпт с текстом пользователя |

---

## Исправленная ошибка из предыдущей версии

**Проблема:** При `/start` приходило сообщение от ветки «подобрать».

**Решение:** Code Router теперь корректно разделяет `callback_query.data` (кнопки) и `message.text` (команды). Вся логика — в одном узле, что исключает ошибки маршрутизации между отдельными If-нодами.

---

## Проверка после импорта

| Действие | Ожидаемый результат |
|----------|---------------------|
| `/start` | Фото + приветствие + 3 кнопки (Каталог, Подобрать, Инфо) |
| Кнопка «📖 Каталог ароматов» | Список категорий с кнопками |
| Кнопка «✨ Подобрать» | AI начинает диалог о подборе аромата |
| Кнопка «🎓 Инфо» | Справка о боте |
| Кнопка «⬅️ Назад» | Возврат в главное меню с фото |
| Категория (🌸/🌲/🌙/🍋) | Поиск в Airtable (нужна настройка) |
| Произвольный текст | AI-ответ от GPT-4o |
