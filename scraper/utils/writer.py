import csv
import json
import os

from scraper.core.config import TEMP_FILE


class CSVWriter:
    """Класс для сохранения данных в CSV-файл с защитой от потери данных."""

    HEADERS: dict[str, str] = {
        "link": "Ссылка",
        "name": "Наименование",
        "price": "Цена",
        "rating": "Рейтинг",
        "description": "Описание",
        "usage": "Инструкция",
        "country": "Страна",
    }

    def __init__(self, filename: str = "products.csv") -> None:
        self.filename: str = filename

    def save_temp(self, products: list[dict[str, str]]) -> None:
        """Сохраняет данные во временный JSON-файл."""
        with open(TEMP_FILE, "w", encoding="utf-8") as file:
            json.dump(products, file, ensure_ascii=False, indent=4)

    def load_temp(self) -> list[dict[str, str]]:
        """Загружает данные из временного JSON-файла."""
        if os.path.exists(TEMP_FILE):
            with open(TEMP_FILE, "r", encoding="utf-8") as file:
                return json.load(file)
        return []

    def write(self, products: list[dict[str, str]]) -> None:
        """Записывает данные в CSV и сохраняет временные файлы."""
        self.save_temp(products)

        with open(self.filename, "w", newline="", encoding="utf-8") as file:
            writer = csv.DictWriter(file, fieldnames=self.HEADERS.keys())
            writer.writerow(self.HEADERS)
            writer.writerows(
                [{k: p.get(k, "N/A") for k in self.HEADERS} for p in products]
            )

        print(f"Данные сохранены в {self.filename}")

        os.remove(TEMP_FILE)
