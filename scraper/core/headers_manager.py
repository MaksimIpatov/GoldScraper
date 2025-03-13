import logging
import random

import requests
from fake_useragent import UserAgent

from .browser import get_cookies
from .config import PERFUME_PAGE_URL


class HeadersManager:
    """Генерирует динамические заголовки и обновляет куки через Playwright."""

    INIT_URL = PERFUME_PAGE_URL

    def __init__(self) -> None:
        self.user_agent = UserAgent()
        self.session = requests.Session()
        self.headers: dict[str, str] = self.generate_headers()
        self.cookies: dict[str, str] = get_cookies()

    def generate_headers(self) -> dict[str, str]:
        """Генерирует случайные заголовки, чтобы имитировать браузер."""
        return {
            "User-Agent": self.user_agent.random,
            "Accept": "application/json, text/plain, */*",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": random.choice(
                ["ru-RU,ru;q=0.9", "en-US,en;q=0.8"]
            ),
            "Referer": self.INIT_URL,
            "Connection": "keep-alive",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-origin",
        }

    def update_cookies(self) -> None:
        """Обновляет куки через Playwright при необходимости."""
        logging.info("Обновляю куки...")
        self.cookies = get_cookies()
        logging.debug(f"Куки обновлены: {self.cookies}")

    def get_headers_and_cookies(self) -> tuple[dict[str, str], dict[str, str]]:
        """Возвращает актуальные заголовки и куки."""
        return self.headers, self.cookies
