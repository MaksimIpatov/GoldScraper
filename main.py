import argparse
import logging

from playwright.sync_api import Page
from tqdm import tqdm

from scraper.core.browser import BrowserManager
from scraper.core.strategies import (
    ProxyScraper,
    ScraperAPIScraper,
    StandardScraper,
)
from scraper.parser import GoldParser
from scraper.scraper import GoldScraper
from scraper.utils.writer import CSVWriter


def setup_logging(verbose: bool) -> None:
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s - %(levelname)s - %(message)s",
        handlers=[logging.FileHandler("scraper.log"), logging.StreamHandler()],
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Gold Apple Scraper")
    parser.add_argument(
        "--scraper",
        choices=["standard", "proxy", "scraperapi"],
        default="standard",
        help="Тип скрапера (standard, proxy, scraperapi)",
    )
    parser.add_argument(
        "--pages",
        type=int,
        default=5,
        help="Количество страниц для парсинга",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Ограничение на количество товаров для парсинга",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Включить подробное логирование",
    )
    args = parser.parse_args()

    setup_logging(args.verbose)
    logging.info("Запуск программы")

    strategy_map = {
        "standard": StandardScraper,
        "proxy": ProxyScraper,
        "scraperapi": ScraperAPIScraper,
    }
    strategy = strategy_map[args.scraper]
    scraper = GoldScraper(
        strategy=strategy(),
        category_id="1000000007",
        city_id="0c5b2444-70a0-4932-980c-b4dc0d3f02b5",
        max_pages=args.pages,
    )
    parser = GoldParser()
    writer = CSVWriter()

    with BrowserManager() as browser:
        logging.info("Сбор списка товаров")
        raw_products: list[dict] = scraper.fetch_products()
        products_to_parse = (
            raw_products[: args.limit] if args.limit else raw_products
        )
        logging.info(f"Парсинг {len(products_to_parse)} товаров")

        parsed_products: list[dict] = [
            parser.parse_product(p) for p in products_to_parse
        ]
        page: Page = browser.new_page()
        for product in tqdm(parsed_products, desc="Парсинг деталей товаров"):
            details: dict[str, str] = scraper.fetch_product_details(
                product["link"],
                page,
            )
            product.update(details)
        page.close()

    logging.info("Запись данных в CSV")
    writer.write(parsed_products)
    logging.info("Программа завершена")


if __name__ == "__main__":
    main()
