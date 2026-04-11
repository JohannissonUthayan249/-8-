# 🐴 Bochka Booking Bot — n8n Workflow

Telegram-бот для записи лошадей в **бочку** (крытый манеж / крытое помещение для верховой езды).

---

## 📋 Описание

Бот управляет записью лошадей на временные слоты с **07:00 до 22:00** (шаг 30 минут, итого 30 слотов в день). Записи хранятся в Google Sheets. Бот поддерживает специальный режим **иппотерапии**: администратор может заблокировать утренние слоты одной командой.

---

## 🤖 Команды бота

| Команда | Описание | Кто может использовать |
|---------|----------|----------------------|
| `/start` | Приветствие и список команд | Все |
| `/schedule` или `/расписание` | Показать расписание на сегодня | Все |
| `/book` или `/запись` | Начать запись (показывает свободные слоты) | Все |
| `/cancel ЧЧ:ММ` | Отменить запись на указанный слот | Все |
| `/hippotherapy ЧЧ:ММ` | Установить время окончания иппотерапии | Администратор |
| `/hippotherapy off` | Снять блокировку иппотерапии | Администратор |

---

## ⚙️ Инструкция по настройке

### 1. Создание Telegram-бота

1. Откройте [@BotFather](https://t.me/BotFather) в Telegram
2. Отправьте команду `/newbot`
3. Введите имя бота (например: `Бочка Запись`)
4. Введите username бота (например: `bochka_booking_bot`)
5. Скопируйте полученный **Bot Token** (вида `1234567890:AAHx...`)

### 2. Настройка Google Sheets

#### Создание таблицы

1. Создайте новую Google Таблицу
2. Переименуйте первый лист в **`Bookings`**
3. Добавьте заголовки в первой строке:
   ```
   A1: date    B1: time    C1: horse_name    D1: booked_by    E1: booked_at
   ```
4. Добавьте второй лист **`Settings`** с заголовками:
   ```
   A1: key    B1: value
   ```
5. Добавьте начальную строку в Settings (для иппотерапии):
   ```
   A2: hippotherapy_end_time    B2: off
   ```
6. Скопируйте **ID таблицы** из URL браузера:
   ```
   https://docs.google.com/spreadsheets/d/[SPREADSHEET_ID]/edit
   ```

#### Подключение Google Sheets к n8n

1. В n8n перейдите в **Settings → Credentials**
2. Нажмите **Add Credential**
3. Выберите **Google Sheets OAuth2 API**
4. Настройте OAuth2 через [Google Cloud Console](https://console.cloud.google.com/):
   - Создайте проект
   - Включите Google Sheets API
   - Создайте OAuth 2.0 Client ID (тип: Web application)
   - Добавьте redirect URI из n8n
5. Вставьте Client ID и Client Secret в n8n, авторизуйтесь

### 3. Импорт workflow в n8n

1. Откройте n8n (обычно `http://localhost:5678`)
2. Нажмите кнопку **+** для создания нового workflow
3. Нажмите **⋯** (меню) → **Import from file**
4. Выберите файл `bochka-booking-bot.json`
5. Workflow будет импортирован со всеми нодами

### 4. Настройка credentials в workflow

После импорта нужно привязать ваши credentials к нодам:

#### Telegram Bot Token

1. В n8n перейдите в **Settings → Credentials → Add Credential**
2. Выберите **Telegram API**
3. Вставьте Bot Token из шага 1
4. Сохраните под именем `Telegram Bot Token`
5. В импортированном workflow все ноды `HTTP Request` уже ссылаются на `telegramApi` — привяжите вашу credential

#### Google Sheets

1. В каждой ноде Google Sheets (их 5: Read Schedule, Write Hippotherapy, Read For Cancel, Update Cancelled, Save Booking):
   - Откройте ноду
   - В поле **Credential** выберите вашу Google Sheets credential
   - В поле **Document ID** замените `YOUR_SPREADSHEET_ID` на ID вашей таблицы

### 5. Запуск

1. Нажмите **Active** (переключатель в правом верхнем углу workflow)
2. Бот начнёт принимать сообщения через Telegram Trigger (встроенный polling/webhook)
3. Проверьте бота, отправив `/start`

---

## 📊 Структура Google Sheets

### Лист `Bookings`

| Колонка | Тип | Описание | Пример |
|---------|-----|----------|--------|
| `date` | Строка | Дата бронирования (ГГГГ-ММ-ДД) | `2026-04-11` |
| `time` | Строка | Время слота (ЧЧ:ММ) | `11:30` |
| `horse_name` | Строка | Имя лошади | `Буран` |
| `booked_by` | Строка | Telegram username или ID | `@ivanov` |
| `booked_at` | Строка | Дата и время записи | `2026-04-11 10:15` |

> При отмене записи поле `horse_name` заменяется на `[ОТМЕНЕНО]`, а слот снова отображается как свободный.

### Лист `Settings`

| Колонка | Описание | Пример |
|---------|----------|--------|
| `key` | Ключ настройки | `hippotherapy_end_time` |
| `value` | Значение | `10:30` или `off` |

---

## 🏥 Как работает иппотерапия

Иппотерапия — это занятия верховой ездой с лечебной целью. Когда в бочке проходит иппотерапия, часть утренних слотов блокируется.

**Установить время окончания:**
```
/hippotherapy 10:30
```
→ Все слоты с 07:00 до 10:00 включительно помечаются как 🏥 Иппотерапия.

**Снять блокировку:**
```
/hippotherapy off
```
→ Все слоты снова становятся доступны.

**Логика сравнения:** слот блокируется если `slot_time < end_time`.  
Пример: при `/hippotherapy 10:30` блокируются 07:00, 07:30, 08:00, 08:30, 09:00, 09:30, 10:00. Слот 10:30 остаётся свободным.

**Хранение:** время иппотерапии хранится в двух местах:
1. **Static Data** workflow (`$getWorkflowStaticData('global').hippEndTime`) — быстрый доступ при генерации расписания
2. **Google Sheets (Settings)** — персистентное хранение, сохраняется при перезапуске n8n

---

## 📱 Поток записи пользователя

```
Пользователь → /book или /schedule
       ↓
Бот показывает расписание с inline-кнопками:
┌──────────────────────────────────┐
│ 📅 Расписание бочки на 11.04.2026│
│                                  │
│ 🏥 07:00 — Иппотерапия           │
│ 🏥 07:30 — Иппотерапия           │
│ 🐴 10:30 — Гром                  │
│ [11:00 — Свободно ✅]  ← кнопка │
│ [11:30 — Свободно ✅]  ← кнопка │
│ [12:00 — Свободно ✅]  ← кнопка │
└──────────────────────────────────┘
       ↓
Пользователь нажимает кнопку [11:00 — Свободно ✅]
       ↓
Бот: "Вы выбрали слот 11:00. Введите имя лошади:"
       ↓
Пользователь пишет: "Буран"
       ↓
Бот: "✅ Лошадь «Буран» записана в бочку на 11:00!"
(запись сохраняется в Google Sheets)
```

---

## 🏗️ Архитектура workflow

```
┌─────────────────┐
│ Telegram Trigger│ ← Получает сообщения и callback_query
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│    Router       │ ← Парсит команды, управляет состоянием
│   (Code node)   │   $getWorkflowStaticData для ожидания имени
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Route Switch   │ ← Маршрутизация по routeType
│  (Switch node)  │
└────────┬────────┘
         │
    ┌────┴────┬────────┬─────────┬──────────┬──────────┐
    │         │        │         │          │          │
    ▼         ▼        ▼         ▼          ▼          ▼
  start   schedule  hippo-   cancel    ask_horse  save_booking
    │         │    therapy      │          │          │
    ▼         ▼        │        ▼          ▼          ▼
Send      Read      Parse   Prepare    Answer    Prepare
Start    Schedule   Hippo   Cancel    Callback   Booking
          │            │        │          │          │
          ▼            ▼        ▼          ▼          ▼
         Build      Write    Read For  Ask Horse    Save
        Schedule    Hippo    Cancel     Name       Booking
          │            │        │                   │
          ▼            ▼        ▼                   ▼
         Send        Send    Cancel              Send Book
        Schedule    Confirm  Booking              Confirm
                               │
                               ▼
                           Update
                          Cancelled
                               │
                               ▼
                           Send Cancel
                            Confirm
```

### Ноды workflow

| № | Нода | Тип | Описание |
|---|------|-----|----------|
| 1 | Telegram Trigger | telegramTrigger | Получает message и callback_query |
| 2 | Router | Code | Парсит команды, управляет состоянием |
| 3 | Route Switch | Switch | Маршрутизирует по 6 веткам |
| 4 | Send Start | HTTP Request | Отправляет приветственное сообщение |
| 5 | Read Schedule | Google Sheets | Читает все записи из Bookings |
| 6 | Build Schedule | Code | Формирует расписание с кнопками |
| 7 | Send Schedule | HTTP Request | Отправляет расписание в Telegram |
| 8 | Parse Hippotherapy | Code | Парсит /hippotherapy команду |
| 9 | Write Hippotherapy | Google Sheets | Сохраняет настройку в Settings |
| 10 | Send Hippo Confirm | HTTP Request | Подтверждает установку иппотерапии |
| 11 | Prepare Cancel | Code | Парсит /cancel команду |
| 12 | Read For Cancel | Google Sheets | Читает записи для поиска отменяемой |
| 13 | Cancel Booking | Code | Находит запись для отмены |
| 14 | Update Cancelled | Google Sheets | Помечает запись как [ОТМЕНЕНО] |
| 15 | Send Cancel Confirm | HTTP Request | Подтверждает отмену |
| 16 | Answer Callback | HTTP Request | Отвечает на callback_query (убирает спиннер) |
| 17 | Ask Horse Name | HTTP Request | Просит ввести имя лошади |
| 18 | Prepare Booking | Code | Подготавливает данные для записи |
| 19 | Save Booking | Google Sheets | Добавляет запись в Bookings |
| 20 | Send Book Confirm | HTTP Request | Подтверждает запись |

---

## 🔧 Технические детали

- **Часовой пояс:** Europe/Moscow (UTC+3) — реализован как смещение `+3h` при формировании дат
- **Хранение состояния:** `$getWorkflowStaticData('global')` — map `{chat_id: selected_time_slot}` для ожидания имени лошади
- **Telegram API:** все вызовы через HTTP Request ноды (не встроенная Telegram нода)
- **Inline кнопки:** `callback_data` формата `book:HH:MM` (например `book:11:30`)
- **Сравнение времени:** строковое сравнение `slot < hippEndTime` работает корректно для формата `HH:MM`

---

## ❓ Частые вопросы

**Q: Бот не отвечает на команды**  
A: Убедитесь, что workflow активирован (переключатель Active включён) и Telegram Trigger настроен с правильным Bot Token.

**Q: Расписание показывает пустые слоты даже когда есть записи**  
A: Проверьте, что в Google Sheets лист называется ровно `Bookings` (с заглавной B) и столбцы называются `date`, `time`, `horse_name`.

**Q: После перезапуска n8n иппотерапия сбросилась**  
A: Static Data сохраняется в БД n8n и восстанавливается автоматически. Если данные потеряны, просто повторно выполните `/hippotherapy ЧЧ:ММ`.

**Q: Как ограничить команду /hippotherapy только для администраторов?**  
A: В ноде `Parse Hippotherapy` добавьте проверку `userId`:
```javascript
const ADMIN_IDS = [123456789]; // ваш Telegram ID
if (!ADMIN_IDS.includes(data.userId)) {
  return [{ json: { chatId, responseText: '❌ У вас нет прав для этой команды.' } }];
}
```

---

## 📝 Лицензия

MIT — используйте и адаптируйте свободно.
