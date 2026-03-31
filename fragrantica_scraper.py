"""
Парсер описаний ароматов с сайта fragrantica.ru.

Извлекает: название, бренд, описание, ноты (верхние, средние, базовые),
основные аккорды, оценку, парфюмера, пол и изображение.

Использование:
    # Парсинг одной страницы аромата:
    python fragrantica_scraper.py https://www.fragrantica.ru/perfume/Dior/Sauvage-31861.html

    # Парсинг нескольких страниц из файла (по одному URL на строку):
    python fragrantica_scraper.py --file urls.txt

    # Сохранение результатов в файл:
    python fragrantica_scraper.py --output results.json URL1 URL2
    python fragrantica_scraper.py --output results.csv URL1 URL2
"""

import argparse
import csv
import json
import os
import re
import sys
import time

import requests
from bs4 import BeautifulSoup


# Задержка между запросами (секунды)
_DEFAULT_DELAY = 2.0

# User-Agent для запросов
_DEFAULT_USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/120.0.0.0 Safari/537.36"
)

_DEFAULT_HEADERS = {
    "User-Agent": _DEFAULT_USER_AGENT,
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "ru-RU,ru;q=0.9,en-US;q=0.5,en;q=0.3",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
}


def fetch_page(url, session=None, delay=_DEFAULT_DELAY):
    """
    Загрузка HTML-страницы по URL.

    Аргументы:
        url: адрес страницы
        session: объект requests.Session (если None — создаётся новый)
        delay: задержка перед запросом в секундах

    Возвращает:
        HTML-содержимое страницы (str).

    Исключения:
        requests.RequestException: при ошибке сети
    """
    if delay > 0:
        time.sleep(delay)

    if session is None:
        session = requests.Session()
        session.headers.update(_DEFAULT_HEADERS)

    response = session.get(url, timeout=30)
    response.raise_for_status()
    response.encoding = "utf-8"
    return response.text


def parse_perfume_page(html):
    """
    Парсинг HTML-страницы аромата с fragrantica.ru.

    Аргументы:
        html: HTML-содержимое страницы (строка)

    Возвращает:
        Словарь с данными аромата:
        {
            "название": str,
            "бренд": str,
            "пол": str,
            "год_выпуска": str,
            "описание": str,
            "парфюмер": str,
            "верхние_ноты": list[str],
            "средние_ноты": list[str],
            "базовые_ноты": list[str],
            "основные_аккорды": list[str],
            "оценка": str,
            "количество_оценок": str,
            "изображение": str,
        }
    """
    soup = BeautifulSoup(html, "html.parser")
    data = {}

    data["название"] = _extract_name(soup)
    data["бренд"] = _extract_brand(soup)
    data["пол"] = _extract_gender(soup)
    data["год_выпуска"] = _extract_year(soup)
    data["описание"] = _extract_description(soup)
    data["парфюмер"] = _extract_perfumer(soup)
    data["верхние_ноты"] = _extract_notes(soup, "top")
    data["средние_ноты"] = _extract_notes(soup, "middle")
    data["базовые_ноты"] = _extract_notes(soup, "base")
    data["основные_аккорды"] = _extract_accords(soup)
    data["оценка"] = _extract_rating(soup)
    data["количество_оценок"] = _extract_rating_count(soup)
    data["изображение"] = _extract_image(soup)

    return data


def _select_first_text(soup, selectors):
    """Попробовать несколько CSS-селекторов, вернуть текст первого найденного."""
    for selector in selectors:
        elem = soup.select_one(selector)
        if elem:
            text = elem.get_text(strip=True)
            if text:
                return text
    return ""


def _extract_name(soup):
    """Извлечение названия аромата."""
    selectors = [
        'h1[itemprop="name"]',
        "h1",
    ]
    text = _select_first_text(soup, selectors)
    if text:
        # Убираем название бренда из заголовка, если оно вначале
        # Формат часто: "Brand Name Perfume Name"
        return text
    return ""


def _extract_brand(soup):
    """Извлечение названия бренда."""
    selectors = [
        '[itemprop="brand"] [itemprop="name"]',
        '[itemprop="brand"]',
        'h1 + p a',
        'p[itemprop="brand"]',
    ]
    return _select_first_text(soup, selectors)


def _extract_gender(soup):
    """Извлечение пола (для кого аромат)."""
    # На fragrantica пол часто указан в тексте рядом с названием
    selectors = [
        'h1 + p small',
        'h1 + p',
    ]
    text = _select_first_text(soup, selectors)
    if text:
        # Ищем ключевые слова
        text_lower = text.lower()
        if "для мужчин и женщин" in text_lower or "унисекс" in text_lower:
            return "унисекс"
        elif "для мужчин" in text_lower:
            return "для мужчин"
        elif "для женщин" in text_lower:
            return "для женщин"
        return text
    return ""


def _extract_year(soup):
    """Извлечение года выпуска."""
    # Год обычно в тексте описания или в блоке с метаинформацией
    selectors = [
        '[itemprop="datePublished"]',
    ]
    text = _select_first_text(soup, selectors)
    if text:
        return text

    # Попробовать найти год в тексте заголовка/подзаголовка
    subtitle = _select_first_text(soup, ['h1 + p'])
    if subtitle:
        match = re.search(r'\b(19|20)\d{2}\b', subtitle)
        if match:
            return match.group(0)

    return ""


def _extract_description(soup):
    """Извлечение описания аромата."""
    selectors = [
        '[itemprop="description"]',
        'div[itemprop="description"]',
        'p[itemprop="description"]',
    ]
    text = _select_first_text(soup, selectors)
    if text:
        return text

    # Запасной вариант — блок с id или class, содержащий описание
    for sel in ['#TextContentP', '.fragrantica-blockquote', '.description-text']:
        elem = soup.select_one(sel)
        if elem:
            return elem.get_text(strip=True)

    return ""


def _extract_perfumer(soup):
    """Извлечение имени парфюмера (нос/создатель)."""
    selectors = [
        '[itemprop="author"]',
        'a[href*="/noses/"]',
    ]
    return _select_first_text(soup, selectors)


def _extract_notes(soup, note_type):
    """
    Извлечение нот аромата.

    note_type: 'top', 'middle', 'base'
    """
    # Fragrantica хранит ноты в блоках pyramid с заголовками
    type_labels = {
        "top": ["верхние ноты", "начальные ноты", "top notes", "верхн"],
        "middle": ["средние ноты", "ноты сердца", "heart notes", "middle notes", "средн"],
        "base": ["базовые ноты", "конечные ноты", "base notes", "базов"],
    }

    labels = type_labels.get(note_type, [])

    # Поиск по заголовку блока нот
    # Часто структура: <b>Верхние ноты</b> <span>нота1, нота2</span>
    for b_tag in soup.find_all(["b", "strong", "h4"]):
        tag_text = b_tag.get_text(strip=True).lower()
        if any(label in tag_text for label in labels):
            # Собираем ноты из следующих элементов
            notes = []
            # Ищем ссылки (ноты часто оформлены как ссылки)
            parent = b_tag.parent
            if parent:
                for a_tag in parent.find_all("a"):
                    note_text = a_tag.get_text(strip=True)
                    if note_text:
                        notes.append(note_text)
                if notes:
                    return notes

                # Если нет ссылок — пробуем span
                for span in parent.find_all("span"):
                    span_text = span.get_text(strip=True)
                    if span_text:
                        notes.extend(
                            n.strip()
                            for n in span_text.split(",")
                            if n.strip()
                        )
                if notes:
                    return notes

    # Поиск по CSS-классам
    class_selectors = {
        "top": [".top-notes", '[data-type="top"]'],
        "middle": [".middle-notes", ".heart-notes", '[data-type="middle"]'],
        "base": [".base-notes", '[data-type="base"]'],
    }

    for selector in class_selectors.get(note_type, []):
        elem = soup.select_one(selector)
        if elem:
            links = elem.find_all("a")
            if links:
                return [a.get_text(strip=True) for a in links if a.get_text(strip=True)]
            text = elem.get_text(strip=True)
            if text:
                return [n.strip() for n in text.split(",") if n.strip()]

    return []


def _extract_accords(soup):
    """Извлечение основных аккордов."""
    selectors = [
        ".accord-bar",
        ".main-accords .accord-bar",
        ".accord-box .accord-bar",
    ]

    accords = []
    for selector in selectors:
        elements = soup.select(selector)
        for elem in elements:
            text = elem.get_text(strip=True)
            if text and text not in accords:
                accords.append(text)
        if accords:
            return accords

    # Запасной вариант — искать блок с аккордами
    accord_div = soup.select_one(".cell.accord")
    if accord_div:
        for item in accord_div.find_all(["span", "div"]):
            text = item.get_text(strip=True)
            if text and text not in accords:
                accords.append(text)

    return accords


def _extract_rating(soup):
    """Извлечение оценки аромата."""
    selectors = [
        '[itemprop="ratingValue"]',
        ".rating-value",
        ".p_fix_ratings span",
    ]
    return _select_first_text(soup, selectors)


def _extract_rating_count(soup):
    """Извлечение количества оценок."""
    selectors = [
        '[itemprop="ratingCount"]',
        ".rating-count",
        '[itemprop="reviewCount"]',
    ]
    return _select_first_text(soup, selectors)


def _extract_image(soup):
    """Извлечение URL изображения аромата."""
    selectors = [
        'img[itemprop="image"]',
        ".perfume-image img",
        'img[src*="mdimg/perfume"]',
    ]
    for selector in selectors:
        elem = soup.select_one(selector)
        if elem:
            src = elem.get("src") or elem.get("data-src", "")
            if src:
                return src
    return ""


def scrape_perfume(url, session=None, delay=_DEFAULT_DELAY):
    """
    Скачать и распарсить страницу аромата.

    Аргументы:
        url: URL страницы аромата на fragrantica.ru
        session: объект requests.Session
        delay: задержка перед запросом

    Возвращает:
        Словарь с данными аромата (+ ключ 'url' с адресом страницы).
    """
    html = fetch_page(url, session=session, delay=delay)
    data = parse_perfume_page(html)
    data["url"] = url
    return data


def scrape_multiple(urls, delay=_DEFAULT_DELAY):
    """
    Парсинг нескольких страниц ароматов.

    Аргументы:
        urls: список URL-адресов
        delay: задержка между запросами

    Возвращает:
        Список словарей с данными ароматов.
    """
    session = requests.Session()
    session.headers.update(_DEFAULT_HEADERS)

    results = []
    for i, url in enumerate(urls, 1):
        print(f"[{i}/{len(urls)}] Парсинг: {url}")
        try:
            data = scrape_perfume(url, session=session, delay=delay)
            results.append(data)
            print(f"  ✓ {data.get('название', 'Без названия')}")
        except requests.RequestException as e:
            print(f"  ✗ Ошибка загрузки: {e}", file=sys.stderr)
        except Exception as e:
            print(f"  ✗ Ошибка парсинга: {e}", file=sys.stderr)

    return results


def save_results(results, filepath):
    """
    Сохранение результатов в файл (JSON или CSV).

    Формат определяется по расширению файла.
    """
    ext = os.path.splitext(filepath)[1].lower()

    if ext == ".json":
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
    elif ext == ".csv":
        if not results:
            return
        # Развернуть списки в строки через запятую
        flat_results = []
        for item in results:
            flat = {}
            for key, value in item.items():
                if isinstance(value, list):
                    flat[key] = ", ".join(value)
                else:
                    flat[key] = value
            flat_results.append(flat)

        fieldnames = list(flat_results[0].keys())
        with open(filepath, "w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(flat_results)
    else:
        raise ValueError(f"Неподдерживаемый формат вывода: {ext}. Используйте .json или .csv")

    print(f"Результаты сохранены в {filepath}")


def main():
    """Точка входа CLI."""
    arg_parser = argparse.ArgumentParser(
        description="Парсер описаний ароматов с fragrantica.ru"
    )
    arg_parser.add_argument(
        "urls",
        nargs="*",
        help="URL-адреса страниц ароматов на fragrantica.ru",
    )
    arg_parser.add_argument(
        "--file",
        "-f",
        help="Файл со списком URL (по одному на строку)",
    )
    arg_parser.add_argument(
        "--output",
        "-o",
        help="Файл для сохранения результатов (.json или .csv)",
    )
    arg_parser.add_argument(
        "--delay",
        "-d",
        type=float,
        default=_DEFAULT_DELAY,
        help=f"Задержка между запросами в секундах (по умолчанию: {_DEFAULT_DELAY})",
    )

    args = arg_parser.parse_args()

    urls = list(args.urls) if args.urls else []

    if args.file:
        if not os.path.isfile(args.file):
            print(f"Ошибка: файл не найден: {args.file}", file=sys.stderr)
            sys.exit(1)
        with open(args.file, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#"):
                    urls.append(line)

    if not urls:
        arg_parser.print_help()
        sys.exit(1)

    results = scrape_multiple(urls, delay=args.delay)

    if args.output:
        save_results(results, args.output)
    else:
        print(json.dumps(results, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
