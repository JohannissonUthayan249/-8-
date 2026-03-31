"""Тесты для модуля парсинга данных."""

import json
import os
import tempfile
import unittest

from parser import (
    detect_format,
    parse_csv,
    parse_file,
    parse_json,
    parse_xml,
)

EXAMPLES_DIR = os.path.join(os.path.dirname(__file__), "..", "examples")


class TestDetectFormat(unittest.TestCase):
    """Тесты определения формата по расширению."""

    def test_json(self):
        self.assertEqual(detect_format("data.json"), "json")

    def test_csv(self):
        self.assertEqual(detect_format("data.csv"), "csv")

    def test_xml(self):
        self.assertEqual(detect_format("data.xml"), "xml")

    def test_unknown(self):
        self.assertIsNone(detect_format("data.txt"))

    def test_no_extension(self):
        self.assertIsNone(detect_format("data"))


class TestParseJSON(unittest.TestCase):
    """Тесты парсинга JSON."""

    def test_parse_example(self):
        filepath = os.path.join(EXAMPLES_DIR, "data.json")
        data = parse_json(filepath)
        self.assertIsInstance(data, list)
        self.assertEqual(len(data), 3)
        self.assertEqual(data[0]["имя"], "Алексей")
        self.assertEqual(data[1]["город"], "Санкт-Петербург")

    def test_parse_dict(self):
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".json", delete=False, encoding="utf-8"
        ) as f:
            json.dump({"ключ": "значение"}, f, ensure_ascii=False)
            f.flush()
            path = f.name
        try:
            data = parse_json(path)
            self.assertIsInstance(data, dict)
            self.assertEqual(data["ключ"], "значение")
        finally:
            os.unlink(path)


class TestParseCSV(unittest.TestCase):
    """Тесты парсинга CSV."""

    def test_parse_example(self):
        filepath = os.path.join(EXAMPLES_DIR, "data.csv")
        data = parse_csv(filepath)
        self.assertIsInstance(data, list)
        self.assertEqual(len(data), 3)
        self.assertEqual(data[0]["имя"], "Алексей")
        self.assertEqual(data[2]["город"], "Новосибирск")

    def test_custom_delimiter(self):
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".csv", delete=False, encoding="utf-8"
        ) as f:
            f.write("имя;возраст\n")
            f.write("Тест;99\n")
            f.flush()
            path = f.name
        try:
            data = parse_csv(path, delimiter=";")
            self.assertEqual(len(data), 1)
            self.assertEqual(data[0]["имя"], "Тест")
            self.assertEqual(data[0]["возраст"], "99")
        finally:
            os.unlink(path)


class TestParseXML(unittest.TestCase):
    """Тесты парсинга XML."""

    def test_parse_example(self):
        filepath = os.path.join(EXAMPLES_DIR, "data.xml")
        data = parse_xml(filepath)
        # Корень — <пользователи>, внутри — список <пользователь>
        self.assertIn("пользователь", data)
        users = data["пользователь"]
        self.assertIsInstance(users, list)
        self.assertEqual(len(users), 3)
        self.assertEqual(users[0]["имя"]["@текст"], "Алексей")

    def test_attributes(self):
        filepath = os.path.join(EXAMPLES_DIR, "data.xml")
        data = parse_xml(filepath)
        users = data["пользователь"]
        self.assertEqual(users[0]["@атрибуты"]["id"], "1")


class TestParseFile(unittest.TestCase):
    """Тесты универсальной функции парсинга."""

    def test_auto_detect_json(self):
        filepath = os.path.join(EXAMPLES_DIR, "data.json")
        data = parse_file(filepath)
        self.assertIsInstance(data, list)
        self.assertEqual(len(data), 3)

    def test_auto_detect_csv(self):
        filepath = os.path.join(EXAMPLES_DIR, "data.csv")
        data = parse_file(filepath)
        self.assertIsInstance(data, list)
        self.assertEqual(len(data), 3)

    def test_auto_detect_xml(self):
        filepath = os.path.join(EXAMPLES_DIR, "data.xml")
        data = parse_file(filepath)
        self.assertIn("пользователь", data)

    def test_explicit_format(self):
        filepath = os.path.join(EXAMPLES_DIR, "data.json")
        data = parse_file(filepath, fmt="json")
        self.assertEqual(len(data), 3)

    def test_file_not_found(self):
        with self.assertRaises(FileNotFoundError):
            parse_file("несуществующий_файл.json")

    def test_unknown_format(self):
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".txt", delete=False
        ) as f:
            f.write("тестовые данные")
            path = f.name
        try:
            with self.assertRaises(ValueError):
                parse_file(path)
        finally:
            os.unlink(path)

    def test_unsupported_format(self):
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".json", delete=False
        ) as f:
            f.write("{}")
            path = f.name
        try:
            with self.assertRaises(ValueError):
                parse_file(path, fmt="yaml")
        finally:
            os.unlink(path)


if __name__ == "__main__":
    unittest.main()
