import logging
import random
from concurrent.futures import ThreadPoolExecutor
from typing import Optional

import requests


class ProxyManager:
    """Класс для автоматического получения и проверки бесплатных прокси."""

    PROXY_SOURCES: list[str] = [
        "https://www.sslproxies.org/",
        "https://free-proxy-list.net/",
        "https://www.proxy-list.download/api/v1/get?type=https",
    ]

    def __init__(self, max_proxies: int = 20, timeout: int = 5) -> None:
        self.max_proxies: int = max_proxies
        self.timeout: int = timeout
        self.proxies: list[str] = []

    def fetch_proxies(self) -> None:
        """Загружает список прокси с разных источников."""
        logging.info("Загружаем список прокси...")
        raw_proxies: set[str] = set()

        for source in self.PROXY_SOURCES:
            try:
                response = requests.get(source, timeout=self.timeout)
                response.raise_for_status()
                extracted_proxies = self.extract_proxies(response.text)
                raw_proxies.update(extracted_proxies)
                logging.info(
                    f"Загружено {len(extracted_proxies)} прокси из {source}"
                )
            except requests.RequestException as e:
                logging.warning(f"Ошибка загрузки прокси с {source}: {e}")

        logging.info(f"Проверяем {len(raw_proxies)} прокси...")
        self.proxies = self.validate_proxies(raw_proxies)
        logging.info(f"Доступно {len(self.proxies)} рабочих HTTPS-прокси.")

    def extract_proxies(self, text: str) -> set[str]:
        """Извлекает IP:PORT из HTML или текстового ответа."""
        return {line.strip() for line in text.split("\n") if ":" in line}

    def validate_proxy(self, proxy) -> Optional[str]:
        """Проверяет доступность прокси через HTTPS."""
        try:
            test_url = "https://httpbin.org/ip"
            response = requests.get(
                test_url,
                proxies={"https": f"http://{proxy}"},
                timeout=self.timeout,
            )
            response.raise_for_status()
            return proxy
        except requests.RequestException:
            return None

    def validate_proxies(self, proxy_list: set[str]) -> list[str]:
        """Проверяет список прокси параллельно."""
        with ThreadPoolExecutor(max_workers=10) as executor:
            valid_proxies = list(
                filter(None, executor.map(self.validate_proxy, proxy_list))
            )
        return valid_proxies[: self.max_proxies]

    def get_proxy(self) -> Optional[str]:
        """Возвращает случайный рабочий прокси."""
        if not self.proxies:
            logging.warning("Нет доступных прокси! Обновляем...")
            self.fetch_proxies()
        return random.choice(self.proxies) if self.proxies else None


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
    )
    manager = ProxyManager()
    manager.fetch_proxies()
    print("✅ Рабочий прокси:", manager.get_proxy())
