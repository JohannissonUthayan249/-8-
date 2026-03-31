# -8-

Парсер данных — модуль для парсинга файлов в форматах JSON, CSV и XML.

## Возможности

- Парсинг **JSON** файлов
- Парсинг **CSV** файлов (с настраиваемым разделителем)
- Парсинг **XML** файлов (с поддержкой атрибутов и вложенных элементов)
- Автоматическое определение формата по расширению файла
- Вывод результата в формате JSON

## Использование

```bash
# Парсинг с автоопределением формата
python parser.py examples/data.json
python parser.py examples/data.csv
python parser.py examples/data.xml

# Указание формата явно
python parser.py --format csv examples/data.csv

# CSV с нестандартным разделителем
python parser.py --delimiter ";" data.csv
```

## Использование как модуля

```python
from parser import parse_file, parse_json, parse_csv, parse_xml

# Универсальный парсинг (формат определяется автоматически)
data = parse_file("examples/data.json")

# Парсинг конкретного формата
data = parse_json("examples/data.json")
data = parse_csv("examples/data.csv", delimiter=",")
data = parse_xml("examples/data.xml")
```

## Запуск тестов

```bash
python -m unittest tests.test_parser -v
```
