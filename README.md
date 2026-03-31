# -8-

Парсер данных — модуль для парсинга файлов и веб-страниц.

## Парсер ароматов fragrantica.ru

Извлекает описания ароматов с сайта [fragrantica.ru](https://www.fragrantica.ru/):
- Название и бренд
- Описание аромата
- Ноты (верхние, средние, базовые)
- Основные аккорды
- Оценка и количество голосов
- Парфюмер
- Изображение

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

# Задержка между запросами (секунды)
python fragrantica_scraper.py --delay 3 URL1 URL2
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
  "название": "Sauvage Dior для мужчин",
  "бренд": "Dior",
  "пол": "для мужчин",
  "год_выпуска": "2015",
  "описание": "Sauvage — это мужской аромат от бренда Dior...",
  "парфюмер": "Франсуа Демаши",
  "верхние_ноты": ["Бергамот", "Перец"],
  "средние_ноты": ["Лаванда", "Герань", "Элеми"],
  "базовые_ноты": ["Амброксан", "Кедр", "Лабданум"],
  "основные_аккорды": ["свежий пряный", "древесный", "ароматический"],
  "оценка": "4.15",
  "количество_оценок": "28450",
  "изображение": "https://fimgs.net/mdimg/perfume/375x500.31861.jpg",
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
