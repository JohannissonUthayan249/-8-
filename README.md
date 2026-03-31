# -8-

Парсер данных — модуль для парсинга файлов и веб-страниц.

## Парсер ароматов fragrantica.ru

Извлекает описания ароматов с сайта [fragrantica.ru](https://www.fragrantica.ru/).

### Целевые поля

| Поле | Описание | Пример |
|------|----------|--------|
| `name` | Название аромата | `Fontainebleau 12 Parfumeurs Francais` |
| `family` | Группа ароматов | `Цветочные`, `Восточные` |
| `notes` | Все ноты через запятую | `ваниль, сандал, кедр, мускус` |
| `classic` | Описание аромата | `Fontainebleau от 12 Parfumeurs Francais...` |

### Защита от ботов

Парсер включает меры обхода защиты от ботов:
- **cloudscraper** — автоматическое решение Cloudflare JavaScript-challenges
- **Ротация User-Agent** — пул из 5 разных браузерных User-Agent
- **Рандомизированные задержки** — случайный разброс ±50% от базовой задержки
- **Retry с экспоненциальным откатом** — до 3 попыток с нарастающей задержкой
- **Sec-Fetch заголовки** — имитация поведения реального браузера

### Установка зависимостей

```bash
pip install -r requirements.txt
```

### Использование из командной строки

```bash
# Парсинг одного аромата
python fragrantica_scraper.py https://www.fragrantica.ru/perfume/Dior/Sauvage-31861.html

# Парсинг нескольких ароматов
python fragrantica_scraper.py URL1 URL2 URL3

# Из файла со списком URL (по одному на строку)
python fragrantica_scraper.py --file urls.txt

# Сохранение в JSON
python fragrantica_scraper.py --output results.json URL

# Сохранение в CSV
python fragrantica_scraper.py --output results.csv URL

# Задержка между запросами (секунды, по умолчанию 4)
python fragrantica_scraper.py --delay 5 URL1 URL2
```

### Использование как модуля

```python
from fragrantica_scraper import scrape_perfume, parse_perfume_page, save_results

# Парсинг страницы аромата по URL
data = scrape_perfume("https://www.fragrantica.ru/perfume/Dior/Sauvage-31861.html")

# Парсинг из уже загруженного HTML
data = parse_perfume_page(html_string)

# Сохранение результатов
save_results([data], "output.json")
save_results([data], "output.csv")
```

### Формат результата

```json
{
  "name": "Sauvage Dior для мужчин",
  "family": "Фужерные",
  "notes": "Бергамот, Перец, Лаванда, Герань, Элеми, Амброксан, Кедр, Лабданум",
  "classic": "Sauvage — это мужской аромат от бренда Dior...",
  "url": "https://www.fragrantica.ru/perfume/Dior/Sauvage-31861.html"
}
```

## Парсер файлов (JSON, CSV, XML)

- Парсинг **JSON** файлов
- Парсинг **CSV** файлов (с настраиваемым разделителем)
- Парсинг **XML** файлов (с поддержкой атрибутов и вложенных элементов)

```bash
python parser.py examples/data.json
python parser.py examples/data.csv
python parser.py examples/data.xml
```

## Запуск тестов

```bash
# Все тесты
python -m unittest discover tests -v

# Тесты парсера fragrantica
python -m unittest tests.test_fragrantica_scraper -v

# Тесты парсера файлов
python -m unittest tests.test_parser -v
```
