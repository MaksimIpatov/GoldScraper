import logging
import random
import re
import time
from typing import Any

from playwright.sync_api import Locator, Page

from .core.strategies import BaseScraper
from scraper.core import DEFAULT_MAX_PAGES, HeadersManager
from scraper.core.config import GOLD_APPLE_API_URL


class GoldScraper:
    """Гибкий скрапер с Playwright для получения деталей товара."""

    def __init__(
        self,
        strategy: BaseScraper,
        category_id: str,
        city_id: str,
        max_pages: int = DEFAULT_MAX_PAGES,
    ) -> None:
        self.scraper = strategy
        self.category_id: str = category_id
        self.city_id: str = city_id
        self.max_pages: int = max_pages
        self.headers_manager = HeadersManager()

    def fetch_products(self) -> list[dict[str, Any]]:
        """Получение списка товаров с API."""
        products: list[dict[str, Any]] = []
        for page in range(1, self.max_pages + 1):
            url: str = (
                f"{GOLD_APPLE_API_URL}/catalog/products?categoryId="
                f"{self.category_id}&pageNumber={page}&cityId={self.city_id}"
            )
            logging.info(f"Запрос страницы {page}: {url}")
            headers, cookies = self.headers_manager.get_headers_and_cookies()
            data = self.scraper.fetch(url, headers=headers, cookies=cookies)
            if not data or "products" not in data.get("data", {}):
                logging.warning(f"Ошибка или пустой ответ на странице {page}")
                break
            products.extend(data["data"]["products"])
            time.sleep(random.uniform(5, 10))
        return products

    def fetch_product_details(
        self, product_url: str, page: Page
    ) -> dict[str, str]:
        """Получение деталей товара через браузер."""
        logging.info(f"Открываю страницу товара: {product_url}")
        usage: str = "N/A"
        country: str = "N/A"
        try:
            self.__load_page(page, product_url)
            country = self.__parse_country(page)
            usage = self.__parse_usage(page)
        except Exception as err_msg:
            logging.error(
                f"Ошибка при парсинге {product_url}: {err_msg}", exc_info=True
            )

        logging.debug(
            f"Результат для {product_url}: usage={usage}, country={country}"
        )
        return {"usage": usage, "country": country}

    def __load_page(self, page: Page, product_url: str) -> None:
        """Загружает страницу товара и ждёт основной контейнер."""
        page.goto(product_url, timeout=60000)
        page.wait_for_load_state("networkidle")
        logging.debug(f"Страница {product_url} успешно загружена")
        try:
            page.wait_for_selector(".bOhy3", timeout=15000)
        except Exception as err_msg:
            logging.debug(
                f"Элемент .bOhy3 не найден, продолжаю парсинг: {err_msg}"
            )

    def __parse_country(self, page: Page) -> str:
        """Извлекает страну происхождения из страницы товара."""
        country: str = "N/A"
        extra_info_tab: Locator = page.locator(
            "button.ga-tabs-tab",
            has_text=re.compile(
                "Дополнительная информация",
                re.IGNORECASE,
            ),
        )
        if extra_info_tab.count() > 0 and extra_info_tab.is_visible():
            extra_info_tab.click()
            page.wait_for_timeout(1000)
            country_locator: Locator = page.locator(
                "div.kDcPG",
                has_text=re.compile(
                    "страна происхождения",
                    re.IGNORECASE,
                ),
            )
            if country_locator.count() > 0:
                full_text: str = country_locator.inner_text()
                country_match = re.search(
                    (
                        r"страна происхождения\s*[\n\r]*(.+?)"
                        r"(?:\s*изготовитель|<br>|$)"
                    ),
                    full_text,
                    re.IGNORECASE | re.DOTALL,
                )
                if country_match:
                    country = country_match.group(1).strip()
                    country = re.split(
                        r"\s*(?:Продавец|изготовитель)", country
                    )[0].strip()
                    logging.debug(f"Извлечённая страна: {country}")
        else:
            country_element: Locator = page.locator(
                (
                    "xpath=//div[contains(text(), 'страна происхождения')]"
                    "/following-sibling::div"
                )
            )
            if country_element.is_visible():
                country = country_element.inner_text().strip()
                logging.debug(f"Извлечённая страна (запасной): {country}")
        return country

    def __parse_usage(self, page: Page) -> str:
        """Извлекает инструкцию по применению из страницы товара."""
        usage: str = "N/A"
        usage_tab: Locator = page.locator(
            "button.ga-tabs-tab",
            has_text=re.compile("Применение", re.IGNORECASE),
        )
        if usage_tab.count() > 0 and usage_tab.is_visible():
            usage_tab.click()
            page.wait_for_timeout(1000)
            usage_locator: Locator = page.locator("div.kDcPG")
            if usage_locator.count() > 0:
                usage = usage_locator.first.inner_text().strip()
        else:
            usage_element: Locator = page.locator(
                "xpath=//div[contains(@class, 'kDcPG')]"
            ).nth(0)
            if usage_element.is_visible():
                usage = usage_element.inner_text().strip()
        return usage
