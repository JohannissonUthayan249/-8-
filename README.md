# -8-
n8n Telegram Bot Workflow

## Описание
n8n воркфлоу для Telegram-бота с функциями подбора и AI-ответов.

### Схема маршрутизации
```
Telegram Trigger → Code Router → If (action == "подобрать"?)
                                   ├─ true  → Code in JavaScript → HTTP Request → Code in JavaScript1 → Telegram API
                                   └─ false → IF AI (action != "/start"?)
                                               ├─ true  → OpenAI Response → Build AI Reply → Telegram AI Reply
                                               └─ false → Telegram API1 (приветствие /start)
```

---

## Проблема
При нажатии на `/start` приходило сообщение с кнопки «подобрать» вместо приветствия.

## Причина
В узле **Code Router** не различались:
- команда `/start` (приходит как `message.text`)
- нажатие кнопки «Подобрать» (приходит как `callback_query.data`)

Оба типа входящих данных записывались в одно поле `action` без проверки источника, и узел **If** не мог корректно их разделить.

---

## Как исправить — пошаговая инструкция

### Шаг 1. Откройте узел «Telegram Trigger»

Убедитесь, что в настройках **Updates** выбраны оба типа:
- ✅ `message`
- ✅ `callback_query`

Это нужно, чтобы бот получал и текстовые команды (`/start`), и нажатия на inline-кнопки (`подобрать`).

---

### Шаг 2. Откройте узел «Code Router» и замените код

Это **главный шаг** — именно здесь была ошибка. Откройте узел **Code Router** (тип: Code) и вставьте этот код:

```javascript
const update = $input.first().json;

let action = '';
let chat_id = '';
let message_text = '';

// 1. Проверяем: это нажатие inline-кнопки (callback_query)?
if (update.body?.callback_query) {
  action = update.body.callback_query.data;          // "подобрать"
  chat_id = update.body.callback_query.message.chat.id;
  message_text = update.body.callback_query.data;

// 2. Или это текстовое сообщение / команда (message)?
} else if (update.body?.message?.text) {
  action = update.body.message.text;                  // "/start"
  chat_id = update.body.message.chat.id;
  message_text = update.body.message.text;
}

return [{ json: { action, chat_id, message_text } }];
```

**Что изменилось:**
- Сначала проверяется `callback_query` — если пользователь нажал кнопку, `action` = `callback_query.data` (например, `"подобрать"`)
- Иначе проверяется `message.text` — если пользователь написал команду, `action` = текст сообщения (например, `"/start"`)
- Порядок `if/else` важен: callback_query проверяется **первым**, потому что при нажатии кнопки Telegram присылает и callback_query, и message одновременно

---

### Шаг 3. Откройте узел «If» и проверьте условие

Убедитесь, что условие настроено так:

| Поле | Значение |
|------|----------|
| **Value 1** | `{{ $json.action }}` |
| **Operation** | `equals` (равно) |
| **Value 2** | `подобрать` |

- ✅ **true** (верхний выход) → идёт в **Code in JavaScript** (ветка подбора)
- ❌ **false** (нижний выход) → идёт в **IF AI**

Если `/start` — action = `"/start"`, что ≠ `"подобрать"` → идёт в false → **IF AI**. Это правильно.

---

### Шаг 4. Откройте узел «IF AI» и проверьте условие

Убедитесь, что условие настроено так:

| Поле | Значение |
|------|----------|
| **Value 1** | `{{ $json.action }}` |
| **Operation** | `not equals` (не равно) |
| **Value 2** | `/start` |

- ✅ **true** (верхний выход) → action ≠ `/start` → пользователь написал произвольный текст → идёт в **OpenAI Response** (AI-ответ)
- ❌ **false** (нижний выход) → action = `/start` → идёт в **Telegram API1** (приветственное сообщение)

---

### Шаг 5. Проверьте узел «Telegram API1» (приветствие)

Убедитесь, что этот узел отправляет приветственное сообщение с кнопкой:

| Параметр | Значение |
|----------|----------|
| **chat_id** | `{{ $json.chat_id }}` |
| **text** | `Добро пожаловать! Выберите действие:` |
| **reply_markup** | `{{ JSON.stringify({inline_keyboard: [[{text: 'Подобрать', callback_data: 'подобрать'}]]}) }}` |

---

### Шаг 6. Проверьте соединения между узлами

Убедитесь, что связи (стрелки) между узлами выглядят так:

```
Telegram Trigger ──→ Code Router ──→ If
                                      ├── true  ──→ Code in JavaScript ──→ HTTP Request ──→ Code in JavaScript1 ──→ Telegram API
                                      └── false ──→ IF AI
                                                     ├── true  ──→ OpenAI Response ──→ Build AI Reply ──→ Telegram AI Reply
                                                     └── false ──→ Telegram API1
```

Если стрелка от **If (false)** идёт куда-то не в **IF AI**, или от **IF AI (false)** не в **Telegram API1** — перетяните её правильно.

---

## Проверка результата

После исправления протестируйте:

| Действие пользователя | Ожидаемый результат |
|-----------------------|---------------------|
| Отправить `/start` | Бот присылает приветствие «Добро пожаловать! Выберите действие:» с кнопкой «Подобрать» |
| Нажать кнопку «Подобрать» | Бот запускает ветку подбора (Code in JavaScript → HTTP Request → ...) |
| Написать произвольный текст | Бот отправляет текст в OpenAI и возвращает AI-ответ |
