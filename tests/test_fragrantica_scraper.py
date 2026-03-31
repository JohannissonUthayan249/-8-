"""Тесты для парсера fragrantica.ru."""

import json
import os
import tempfile
import unittest

from fragrantica_scraper import (
    _extract_accords,
    _extract_brand,
    _extract_description,
    _extract_gender,
    _extract_image,
    _extract_name,
    _extract_notes,
    _extract_perfumer,
    _extract_rating,
    _extract_rating_count,
    _extract_year,
    parse_perfume_page,
    save_results,
)

# Имитация HTML-страницы аромата fragrantica.ru
SAMPLE_PERFUME_HTML = """
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <title>Sauvage Dior — аромат для мужчин 2015</title>
</head>
<body>
<div id="col1">
    <div class="perfume-header">
        <h1 itemprop="name">Sauvage Dior для мужчин</h1>
        <p>
            <span itemprop="brand" itemscope>
                <a href="/designers/Dior.html">
                    <span itemprop="name">Dior</span>
                </a>
            </span>
            <small>для мужчин</small>
        </p>
    </div>

    <div class="perfume-image">
        <img itemprop="image" src="https://fimgs.net/mdimg/perfume/375x500.31861.jpg" alt="Sauvage Dior">
    </div>

    <div itemprop="description">
        <p>Sauvage — это мужской аромат от бренда Dior, выпущенный в 2015 году.
        Парфюмер — Франсуа Демаши. Аромат свежий, пряный и древесный.</p>
    </div>

    <div>
        <b>Парфюмер: </b>
        <a href="/noses/Francois-Demachy.html" itemprop="author">Франсуа Демаши</a>
    </div>

    <div itemprop="aggregateRating" itemscope>
        <span itemprop="ratingValue">4.15</span> из 5
        (<span itemprop="ratingCount">28450</span> оценок)
    </div>

    <div class="notes-pyramid">
        <div>
            <b>Верхние ноты:</b>
            <span>
                <a href="/notes/Bergamot.html">Бергамот</a>,
                <a href="/notes/Pepper.html">Перец</a>
            </span>
        </div>
        <div>
            <b>Средние ноты:</b>
            <span>
                <a href="/notes/Lavender.html">Лаванда</a>,
                <a href="/notes/Geranium.html">Герань</a>,
                <a href="/notes/Elemi.html">Элеми</a>
            </span>
        </div>
        <div>
            <b>Базовые ноты:</b>
            <span>
                <a href="/notes/Ambroxan.html">Амброксан</a>,
                <a href="/notes/Cedar.html">Кедр</a>,
                <a href="/notes/Labdanum.html">Лабданум</a>
            </span>
        </div>
    </div>

    <div class="main-accords">
        <div class="accord-bar">свежий пряный</div>
        <div class="accord-bar">древесный</div>
        <div class="accord-bar">ароматический</div>
        <div class="accord-bar">цитрусовый</div>
    </div>
</div>
</body>
</html>
"""

# Минимальный HTML — пустая страница без данных
MINIMAL_HTML = """
<!DOCTYPE html>
<html><head><title>Test</title></head>
<body><div>Пусто</div></body></html>
"""

# HTML с частичными данными
PARTIAL_HTML = """
<!DOCTYPE html>
<html lang="ru">
<head><title>Тест</title></head>
<body>
    <h1 itemprop="name">Bleu de Chanel</h1>
    <div itemprop="description">Ароматический древесный аромат для мужчин.</div>
    <div>
        <span itemprop="ratingValue">4.30</span>
    </div>
</body>
</html>
"""


class TestParseName(unittest.TestCase):
    """Тесты извлечения названия."""

    def test_extract_name(self):
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(SAMPLE_PERFUME_HTML, "html.parser")
        name = _extract_name(soup)
        self.assertIn("Sauvage", name)

    def test_extract_name_empty(self):
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(MINIMAL_HTML, "html.parser")
        name = _extract_name(soup)
        # Даже минимальный HTML имеет какой-то контент — не сломается
        self.assertIsInstance(name, str)


class TestParseBrand(unittest.TestCase):
    """Тесты извлечения бренда."""

    def test_extract_brand(self):
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(SAMPLE_PERFUME_HTML, "html.parser")
        brand = _extract_brand(soup)
        self.assertEqual(brand, "Dior")

    def test_extract_brand_missing(self):
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(MINIMAL_HTML, "html.parser")
        brand = _extract_brand(soup)
        self.assertEqual(brand, "")


class TestParseGender(unittest.TestCase):
    """Тесты извлечения пола."""

    def test_extract_gender_male(self):
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(SAMPLE_PERFUME_HTML, "html.parser")
        gender = _extract_gender(soup)
        self.assertEqual(gender, "для мужчин")

    def test_extract_gender_missing(self):
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(MINIMAL_HTML, "html.parser")
        gender = _extract_gender(soup)
        self.assertEqual(gender, "")


class TestParseDescription(unittest.TestCase):
    """Тесты извлечения описания."""

    def test_extract_description(self):
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(SAMPLE_PERFUME_HTML, "html.parser")
        desc = _extract_description(soup)
        self.assertIn("Sauvage", desc)
        self.assertIn("2015", desc)
        self.assertIn("Франсуа Демаши", desc)

    def test_extract_description_missing(self):
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(MINIMAL_HTML, "html.parser")
        desc = _extract_description(soup)
        self.assertEqual(desc, "")


class TestParsePerfumer(unittest.TestCase):
    """Тесты извлечения парфюмера."""

    def test_extract_perfumer(self):
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(SAMPLE_PERFUME_HTML, "html.parser")
        perfumer = _extract_perfumer(soup)
        self.assertEqual(perfumer, "Франсуа Демаши")


class TestParseNotes(unittest.TestCase):
    """Тесты извлечения нот."""

    def test_top_notes(self):
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(SAMPLE_PERFUME_HTML, "html.parser")
        notes = _extract_notes(soup, "top")
        self.assertIn("Бергамот", notes)
        self.assertIn("Перец", notes)

    def test_middle_notes(self):
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(SAMPLE_PERFUME_HTML, "html.parser")
        notes = _extract_notes(soup, "middle")
        self.assertIn("Лаванда", notes)
        self.assertIn("Герань", notes)
        self.assertIn("Элеми", notes)

    def test_base_notes(self):
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(SAMPLE_PERFUME_HTML, "html.parser")
        notes = _extract_notes(soup, "base")
        self.assertIn("Амброксан", notes)
        self.assertIn("Кедр", notes)
        self.assertIn("Лабданум", notes)

    def test_empty_notes(self):
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(MINIMAL_HTML, "html.parser")
        notes = _extract_notes(soup, "top")
        self.assertEqual(notes, [])


class TestParseAccords(unittest.TestCase):
    """Тесты извлечения аккордов."""

    def test_extract_accords(self):
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(SAMPLE_PERFUME_HTML, "html.parser")
        accords = _extract_accords(soup)
        self.assertEqual(len(accords), 4)
        self.assertIn("свежий пряный", accords)
        self.assertIn("древесный", accords)

    def test_empty_accords(self):
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(MINIMAL_HTML, "html.parser")
        accords = _extract_accords(soup)
        self.assertEqual(accords, [])


class TestParseRating(unittest.TestCase):
    """Тесты извлечения оценки."""

    def test_extract_rating(self):
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(SAMPLE_PERFUME_HTML, "html.parser")
        rating = _extract_rating(soup)
        self.assertEqual(rating, "4.15")

    def test_extract_rating_count(self):
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(SAMPLE_PERFUME_HTML, "html.parser")
        count = _extract_rating_count(soup)
        self.assertEqual(count, "28450")


class TestParseImage(unittest.TestCase):
    """Тесты извлечения изображения."""

    def test_extract_image(self):
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(SAMPLE_PERFUME_HTML, "html.parser")
        img = _extract_image(soup)
        self.assertIn("31861", img)
        self.assertTrue(img.startswith("https://"))


class TestParsePerfumePage(unittest.TestCase):
    """Тесты полного парсинга страницы."""

    def test_full_parse(self):
        data = parse_perfume_page(SAMPLE_PERFUME_HTML)
        self.assertIn("Sauvage", data["название"])
        self.assertEqual(data["бренд"], "Dior")
        self.assertEqual(data["пол"], "для мужчин")
        self.assertIn("Sauvage", data["описание"])
        self.assertEqual(data["парфюмер"], "Франсуа Демаши")
        self.assertIn("Бергамот", data["верхние_ноты"])
        self.assertIn("Лаванда", data["средние_ноты"])
        self.assertIn("Амброксан", data["базовые_ноты"])
        self.assertEqual(len(data["основные_аккорды"]), 4)
        self.assertEqual(data["оценка"], "4.15")
        self.assertEqual(data["количество_оценок"], "28450")
        self.assertTrue(data["изображение"].startswith("https://"))

    def test_partial_parse(self):
        data = parse_perfume_page(PARTIAL_HTML)
        self.assertIn("Bleu de Chanel", data["название"])
        self.assertIn("древесный", data["описание"])
        self.assertEqual(data["оценка"], "4.30")
        # Ноты и аккорды отсутствуют
        self.assertEqual(data["верхние_ноты"], [])
        self.assertEqual(data["основные_аккорды"], [])

    def test_empty_page(self):
        data = parse_perfume_page(MINIMAL_HTML)
        # Не падает, возвращает пустые значения
        self.assertIsInstance(data, dict)
        self.assertIn("название", data)
        self.assertIn("описание", data)

    def test_all_keys_present(self):
        """Проверяем, что все ожидаемые ключи присутствуют."""
        data = parse_perfume_page(MINIMAL_HTML)
        expected_keys = [
            "название", "бренд", "пол", "год_выпуска", "описание",
            "парфюмер", "верхние_ноты", "средние_ноты", "базовые_ноты",
            "основные_аккорды", "оценка", "количество_оценок", "изображение",
        ]
        for key in expected_keys:
            self.assertIn(key, data)


class TestSaveResults(unittest.TestCase):
    """Тесты сохранения результатов."""

    def _get_sample_data(self):
        return [parse_perfume_page(SAMPLE_PERFUME_HTML)]

    def test_save_json(self):
        data = self._get_sample_data()
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".json", delete=False, encoding="utf-8"
        ) as f:
            path = f.name

        try:
            save_results(data, path)
            with open(path, "r", encoding="utf-8") as f:
                loaded = json.load(f)
            self.assertEqual(len(loaded), 1)
            self.assertIn("Sauvage", loaded[0]["название"])
        finally:
            os.unlink(path)

    def test_save_csv(self):
        data = self._get_sample_data()
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".csv", delete=False, encoding="utf-8"
        ) as f:
            path = f.name

        try:
            save_results(data, path)
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()
            self.assertIn("Sauvage", content)
            self.assertIn("Dior", content)
        finally:
            os.unlink(path)

    def test_save_unsupported_format(self):
        data = self._get_sample_data()
        with self.assertRaises(ValueError):
            save_results(data, "/tmp/test.xyz")


class TestGenderExtraction(unittest.TestCase):
    """Тесты извлечения разных вариантов пола."""

    def test_unisex(self):
        from bs4 import BeautifulSoup
        html = '<html><body><h1>Test</h1><p><small>для мужчин и женщин</small></p></body></html>'
        soup = BeautifulSoup(html, "html.parser")
        self.assertEqual(_extract_gender(soup), "унисекс")

    def test_female(self):
        from bs4 import BeautifulSoup
        html = '<html><body><h1>Test</h1><p><small>для женщин</small></p></body></html>'
        soup = BeautifulSoup(html, "html.parser")
        self.assertEqual(_extract_gender(soup), "для женщин")


if __name__ == "__main__":
    unittest.main()
