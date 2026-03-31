"""
Модуль парсинга данных.

Поддерживаемые форматы:
  - JSON
  - CSV
  - XML

Использование:
  python parser.py <путь_к_файлу>
  python parser.py --format json <путь_к_файлу>
"""

import argparse
import csv
import json
import os
import sys
import xml.etree.ElementTree as ET


def parse_json(filepath):
    """Парсинг JSON-файла. Возвращает словарь или список."""
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)


def parse_csv(filepath, delimiter=","):
    """Парсинг CSV-файла. Возвращает список словарей (каждая строка — словарь)."""
    with open(filepath, "r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f, delimiter=delimiter)
        return list(reader)


def parse_xml(filepath):
    """Парсинг XML-файла. Возвращает словарь с данными из дерева элементов."""
    tree = ET.parse(filepath)
    root = tree.getroot()
    return _xml_element_to_dict(root)


def _xml_element_to_dict(element):
    """Рекурсивное преобразование XML-элемента в словарь."""
    result = {}

    # Атрибуты элемента
    if element.attrib:
        result["@атрибуты"] = dict(element.attrib)

    # Текст элемента
    text = element.text
    if text and text.strip():
        result["@текст"] = text.strip()

    # Дочерние элементы
    children = list(element)
    if children:
        child_dict = {}
        for child in children:
            child_data = _xml_element_to_dict(child)
            tag = child.tag
            if tag in child_dict:
                # Если тег уже есть — собираем в список
                if not isinstance(child_dict[tag], list):
                    child_dict[tag] = [child_dict[tag]]
                child_dict[tag].append(child_data)
            else:
                child_dict[tag] = child_data
        result.update(child_dict)

    return result


def detect_format(filepath):
    """Определение формата файла по расширению."""
    ext = os.path.splitext(filepath)[1].lower()
    format_map = {
        ".json": "json",
        ".csv": "csv",
        ".xml": "xml",
    }
    return format_map.get(ext)


def parse_file(filepath, fmt=None, csv_delimiter=","):
    """
    Универсальный парсинг файла.

    Аргументы:
        filepath: путь к файлу
        fmt: формат файла ('json', 'csv', 'xml'). Если None — определяется автоматически.
        csv_delimiter: разделитель для CSV (по умолчанию ',')

    Возвращает:
        Распарсенные данные (словарь или список).

    Исключения:
        FileNotFoundError: если файл не найден
        ValueError: если формат не распознан
    """
    if not os.path.isfile(filepath):
        raise FileNotFoundError(f"Файл не найден: {filepath}")

    if fmt is None:
        fmt = detect_format(filepath)

    if fmt is None:
        raise ValueError(
            f"Не удалось определить формат файла: {filepath}. "
            "Укажите формат явно с помощью параметра --format."
        )

    parsers = {
        "json": lambda: parse_json(filepath),
        "csv": lambda: parse_csv(filepath, delimiter=csv_delimiter),
        "xml": lambda: parse_xml(filepath),
    }

    parser_func = parsers.get(fmt)
    if parser_func is None:
        raise ValueError(
            f"Неподдерживаемый формат: {fmt}. "
            f"Доступные форматы: {', '.join(parsers.keys())}"
        )

    return parser_func()


def main():
    """Точка входа при запуске из командной строки."""
    arg_parser = argparse.ArgumentParser(
        description="Парсер данных — поддержка JSON, CSV, XML"
    )
    arg_parser.add_argument("filepath", help="Путь к файлу для парсинга")
    arg_parser.add_argument(
        "--format",
        "-f",
        choices=["json", "csv", "xml"],
        default=None,
        help="Формат файла (если не указан — определяется по расширению)",
    )
    arg_parser.add_argument(
        "--delimiter",
        "-d",
        default=",",
        help="Разделитель для CSV-файлов (по умолчанию: запятая)",
    )

    args = arg_parser.parse_args()

    try:
        data = parse_file(args.filepath, fmt=args.format, csv_delimiter=args.delimiter)
        # Выводим результат в формате JSON с отступами
        print(json.dumps(data, ensure_ascii=False, indent=2))
    except (FileNotFoundError, ValueError) as e:
        print(f"Ошибка: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
