import logging
import re
from typing import Any

from playwright.sync_api import Page

__all__ = ["GoldParser"]


class GoldParser:
    """Парсер данных из JSON-ответов API и HTML-страниц товара."""

    @staticmethod
    def parse_product(product: dict[str, Any]) -> dict[str, str]:
        """Извлекает основные данные из списка товаров."""
        return {
            "link": f"https://goldapple.ru{product.get('url', '')}",
            "name": (
                f"{product.get('brand', '')} "
                f"{product.get('name', '')}".strip()
            ),
            "price": product.get("price", {})
            .get("actual", {})
            .get("amount", "N/A"),
            "rating": product.get("reviews", {}).get("rating", "N/A"),
            "description": product.get("productType", "N/A"),
            "usage": "N/A",
            "country": "N/A",
        }

    @staticmethod
    def parse_product_details(page: Page) -> dict[str, str]:
        """Извлекает инструкцию по применению и страну производства."""
        usage: str = "N/A"
        country: str = "N/A"

        try:
            page.wait_for_selector(".bOhy3", timeout=10000)
            extra_info_tab = page.locator(
                "button.ga-tabs-tab",
                has_text=re.compile(
                    "Дополнительная информация", re.IGNORECASE
                ),
            )
            if extra_info_tab.is_visible():
                extra_info_tab.click()
                page.wait_for_timeout(1000)

            country_locator = page.locator(
                "div.kDcPG",
                has_text=re.compile("страна происхождения", re.IGNORECASE),
            )
            if country_locator.count() > 0:
                full_text = country_locator.inner_text()
                country_match = re.search(
                    r"страна происхождения\s*[\n\r]*(.+?)"
                    r"(?:\s*изготовитель|<br>|$)",
                    full_text,
                    re.IGNORECASE | re.DOTALL,
                )
                if country_match:
                    country = country_match.group(1).strip()
                    country = re.split(
                        r"\s*(?:Продавец|изготовитель)", country
                    )[0].strip()

            usage_tab = page.locator(
                "button.ga-tabs-tab",
                has_text=re.compile("Применение", re.IGNORECASE),
            )
            if usage_tab.is_visible():
                usage_tab.click()
                page.wait_for_timeout(1000)
                usage_locator = page.locator("div.kDcPG")
                if usage_locator.count() > 0:
                    usage = usage_locator.first.inner_text().strip()
        except Exception as err_msg:
            logging.debug(f"Ошибка парсинга деталей: {err_msg}")
        return {"usage": usage, "country": country}
