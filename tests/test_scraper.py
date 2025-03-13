from scraper.core.strategies import StandardScraper
from scraper.scraper import GoldScraper


def test_scraper_init(mocker):
    """Тест инициализации GoldScraper."""
    mocker.patch("scraper.core.headers_manager.HeadersManager")
    scraper = GoldScraper(
        strategy=StandardScraper(),
        category_id="test_cat",
        city_id="test_city",
        max_pages=2,
    )
    assert scraper.category_id == "test_cat"
    assert scraper.city_id == "test_city"
    assert scraper.max_pages == 2


def test_fetch_products(mocker):
    """Тест получения списка товаров."""
    mocker.patch(
        "scraper.core.headers_manager.HeadersManager.get_headers_and_cookies",
        return_value=({}, {}),
    )
    mock_strategy = mocker.patch.object(StandardScraper, "fetch")
    mock_strategy.return_value = {"data": {"products": [{"id": 1}, {"id": 2}]}}

    scraper = GoldScraper(
        strategy=StandardScraper(),
        category_id="test",
        city_id="test",
        max_pages=1,
    )
    products = scraper.fetch_products()
    assert len(products) == 2
    assert products[0]["id"] == 1
