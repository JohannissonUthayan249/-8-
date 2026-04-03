# Telegram Perfume Bot — n8n Workflow

## Где ошибка

Твой текущий workflow использует **два If-нода** (`If` + `IF AI`) для маршрутизации:

```
Code Router → If
  true  → Code in JavaScript → HTTP Request → ... (Airtable — ароматы)
  false → IF AI
    true  → OpenAI → AI Reply
    false → Telegram API1 (приветствие с фото)
```

**Проблема:** нода `If` проверяет условие неправильно — `/start` попадает в ветку `true` (Airtable), вместо того чтобы идти в `false` → `IF AI` → `false` → `Telegram API1` (фото приветствия).

Когда пользователь нажимает `/start`, он получает **картинки ароматов из Airtable** вместо **приветственного фото**.

---

## Что заменить

Удали **обе** ноды `If` и `IF AI` и замени их **одной** нодой **Switch** (тип `n8n-nodes-base.switch`, версия 3).

### Новая схема:

```
Telegram Trigger → Code Router → Switch
  Output 0 (start)  → Telegram API1   (sendPhoto — приветствие)
  Output 1 (select) → Code in JavaScript → HTTP Request → ... (Airtable)
  Output 2 (fallback) → OpenAI Response → Build AI Reply → Telegram AI Reply
```

---

## Как настроить ноду Switch в n8n

### Шаг 1: Удали ноды `If` и `IF AI`

### Шаг 2: Добавь ноду `Switch` (версия 3) и настрой:

**Rule 0 — "start":**
- Left Value: `{{ $json.action }}`
- Operation: **Equals**
- Right Value: `/start`
- Rename Output: ✅ → `start`

**Rule 1 — "select":**
- Left Value: `{{ $json.action }}`
- Operation: **Equals**
- Right Value: `подобрать`
- Rename Output: ✅ → `select`

**Fallback Output:** `Extra Output` (для всего остального → AI)

### Шаг 3: Подключи выходы:

| Выход Switch | Куда подключить |
|---|---|
| Output 0 (`start`) | **Telegram API1** (sendPhoto) |
| Output 1 (`select`) | **Code in JavaScript** (Airtable flow) |
| Output 2 (`fallback`) | **OpenAI Response** |

### Шаг 4: В ноде Build AI Reply замени ссылку

Если у тебя в **Build AI Reply** есть строка:
```
$('If').first().json.chatId
```
или
```
$('IF AI').first().json.chatId
```

Замени на:
```
$('Switch').first().json.chatId
```

---

## Готовый workflow (копируй и вставляй)

Файл `n8n_workflow.json` содержит полный готовый workflow.

**Как импортировать в n8n:**
1. Открой n8n
2. Меню → **Import from File**
3. Выбери файл `n8n_workflow.json`
4. Привяжи свои credentials (Telegram API, Airtable, OpenAI)
5. Замени `YOUR_WELCOME_PHOTO_URL` на URL твоего фото
6. Замени `YOUR_BASE_ID` и `YOUR_TABLE_NAME` на данные Airtable

---

## Код ноды Code Router (для копирования)

```javascript
const update = $input.first().json;
let action = '';
let chatId = '';
let text = '';

if (update.body?.callback_query) {
  action = update.body.callback_query.data || '';
  chatId = String(update.body.callback_query.message.chat.id);
} else if (update.body?.message) {
  text = (update.body.message.text || '').trim();
  chatId = String(update.body.message.chat.id);
  action = text;
}

return [{ json: { action, chatId, text } }];
```

## Код ноды Build AI Reply (для копирования)

```javascript
const chatId = $('Switch').first().json.chatId;
const aiReply = $json.choices?.[0]?.message?.content || 'Извините, не удалось получить ответ.';

return [{ json: { chatId, text: aiReply } }];
```
