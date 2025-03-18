import logging
from typing import Optional

from playwright.sync_api import (
    Browser,
    BrowserContext,
    Page,
    Playwright,
    sync_playwright,
)

from .config import PERFUME_PAGE_URL


class BrowserManager:
    def __init__(self, headless: bool = True) -> None:
        self.headless: bool = headless
        self.playwright: Optional[Playwright] = None
        self.browser: Optional[Browser] = None
        self.context: BrowserContext

    def __enter__(self) -> "BrowserManager":
        self.playwright = sync_playwright().start()
        self.browser = self.playwright.chromium.launch(headless=self.headless)
        self.context = self.browser.new_context()
        return self

    def new_page(self) -> Page:
        return self.context.new_page()

    def __exit__(
        self,
        exc_type: Optional[type],
        exc_value: Optional[Exception],
        traceback: Optional[object],
    ) -> None:
        if self.browser:
            self.browser.close()
        if self.playwright:
            self.playwright.stop()
        logging.info("Браузер Playwright закрыт.")


def get_cookies() -> dict[str, str]:
    """Открывает браузер, заходит на сайт и получает свежие куки."""
    with sync_playwright() as p:
        browser: Browser = p.chromium.launch(headless=False)
        context: BrowserContext = browser.new_context()
        page: Page = context.new_page()
        try:
            logging.info("Обновление кук...")
            page.goto(PERFUME_PAGE_URL, timeout=60000)
            page.wait_for_timeout(5000)
            cookies = context.cookies()
            browser.close()
            logging.info("Куки обновлены.")
            return {cookie["name"]: cookie["value"] for cookie in cookies}
        except Exception as e:
            logging.error(f"Ошибка при получении кук: {e}")
            browser.close()
            return {}


def fetch_product_details_via_browser(product_url: str) -> dict[str, str]:
    """Открывает браузер и извлекает детали товара."""
    with sync_playwright() as p:
        browser: Browser = p.chromium.launch(headless=True)
        context: BrowserContext = browser.new_context()
        page: Page = context.new_page()
        try:
            logging.info(f"Открываем страницу товара: {product_url}")
            page.goto(product_url, timeout=60000)
            page.wait_for_load_state("networkidle")
            usage: str = "N/A"
            try:
                usage_element = page.locator(
                    "xpath=//div[contains(@class, 'kDcPG')]"
                ).nth(0)
                if usage_element.is_visible():
                    usage = usage_element.inner_text().strip()
            except Exception as err_msg:
                logging.debug(
                    f"Не удалось найти информацию о применении {err_msg}"
                )
            country: str = "N/A"
            try:
                country_element = page.locator(
                    "xpath=//div[contains(text(), "
                    "'страна происхождения')]/following-sibling::div"
                )
                if country_element.is_visible():
                    country = country_element.inner_text().strip()
            except Exception as err_msg:
                logging.debug(
                    f"Не удалось найти страну происхождения {err_msg}"
                )
            browser.close()
            return {"usage": usage, "country": country}
        except Exception as err_msg:
            logging.error(f"Ошибка при получении деталей товара: {err_msg}")
            browser.close()
            return {"usage": "N/A", "country": "N/A"}
