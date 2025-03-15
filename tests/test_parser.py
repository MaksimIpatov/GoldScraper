import string

import pytest
from playwright.sync_api import sync_playwright

from scraper.parser import GoldParser


def test_parse_product():
    """Тест парсинга основных данных продукта."""
    product = {
        "url": "/test-product",
        "brand": "TestBrand",
        "name": "TestName",
        "price": {"actual": {"amount": "1000"}},
        "reviews": {"rating": "4.5"},
        "productType": "Perfume",
    }
    result = GoldParser.parse_product(product)
    assert result["link"] == "https://goldapple.ru/test-product"
    assert result["name"] == "TestBrand TestName"
    assert result["price"] == "1000"
    assert result["rating"] == "4.5"
    assert result["description"] == "Perfume"
    assert result["usage"] == "N/A"
    assert result["country"] == "N/A"


def test_parse_product_missing_fields():
    """Тест парсинга продукта с отсутствующими полями."""
    product = {}
    result = GoldParser.parse_product(product)
    assert result["link"] == "https://goldapple.ru"
    assert result["name"] == ""
    assert result["price"] == "N/A"
    assert result["rating"] == "N/A"
    assert result["description"] == "N/A"


@pytest.mark.playwright
def test_parse_product_details(mocker):
    """Тест парсинга деталей продукта с Playwright."""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        page.set_content(
            """
            <div class="bOhy3">
                <button class="ga-tabs-tab">Дополнительная информация</button>
                <div class="kDcPG">Страна происхождения: Франция</div>
            </div>
        """
        )

        mocker.patch.object(page, "wait_for_selector", return_value=None)
        mocker.patch.object(
            page.locator("button.ga-tabs-tab").nth(0),
            "is_visible",
            return_value=True,
        )

        result = GoldParser.parse_product_details(page)
        assert result["country"].strip(string.punctuation + " ") == "Франция"

        browser.close()
