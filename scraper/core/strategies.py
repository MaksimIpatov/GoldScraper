import logging
from typing import Any, Optional

import requests

from .config import (
    DEFAULT_TIMEOUT,
    PROXY_SCRAPER_TIME_OUT,
    SCRAPER_API_KEY,
    SCRAPER_API_TIME_OUT,
)
from .proxy_manager import ProxyManager


class BaseScraper:
    """Базовый класс для всех стратегий скрапинга."""

    def __init__(self) -> None:
        self.session = requests.Session()

    def fetch(
        self, url: str, headers: dict[str, str], cookies: dict[str, str]
    ) -> Optional[dict[str, Any]]:
        raise NotImplementedError(
            "Метод fetch() должен быть реализован в подклассах."
        )


class StandardScraper(BaseScraper):
    """Прямой запрос без прокси."""

    def fetch(
        self, url: str, headers: dict[str, str], cookies: dict[str, str]
    ) -> Optional[dict[str, Any]]:
        try:
            response = self.session.get(
                url, headers=headers, cookies=cookies, timeout=DEFAULT_TIMEOUT
            )
            response.raise_for_status()
            return response.json()
        except requests.RequestException as err_msg:
            logging.warning(f"Ошибка запроса: {err_msg}")
            return None


class ProxyScraper(BaseScraper):
    """Скрапинг через проверенные прокси."""

    def __init__(self) -> None:
        super().__init__()
        self.proxy_manager = ProxyManager()
        self.proxy_manager.fetch_proxies()

    def fetch(
        self, url: str, headers: dict[str, str], cookies: dict[str, str]
    ) -> Optional[dict[str, Any]]:
        proxy = self.proxy_manager.get_proxy()
        if not proxy:
            logging.error("Нет рабочих прокси!")
            return None
        try:
            response = self.session.get(
                url,
                headers=headers,
                cookies=cookies,
                proxies={"http": proxy, "https": proxy},
                timeout=PROXY_SCRAPER_TIME_OUT,
            )
            response.raise_for_status()
            return response.json()
        except requests.RequestException as err_msg:
            logging.warning(f"Ошибка прокси ({proxy}): {err_msg}")
            return None


class ScraperAPIScraper(BaseScraper):
    """Использование ScraperAPI."""

    BASE_URL: str = "http://api.scraperapi.com"

    def fetch(
        self, url: str, headers: dict[str, str], cookies: dict[str, str]
    ) -> Optional[dict[str, Any]]:
        params = {
            "api_key": SCRAPER_API_KEY,
            "url": url,
            "keep_headers": "true",
            "render": "true",
        }
        try:
            response = self.session.get(
                self.BASE_URL,
                params=params,
                headers=headers,
                cookies=cookies,
                timeout=SCRAPER_API_TIME_OUT,
            )
            response.raise_for_status()
            logging.debug(f"Ответ ScraperAPI: {response.text[:200]}")
            return response.json()
        except requests.RequestException as err_msg:
            logging.warning(f"Ошибка ScraperAPI: {err_msg}")
            return None
