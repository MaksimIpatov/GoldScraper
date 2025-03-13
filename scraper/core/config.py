from decouple import config

PERFUME_PAGE_URL: str = "https://goldapple.ru/parfjumerija"
GOLD_APPLE_API_URL: str = "https://goldapple.ru/front/api"
PRODUCT_DETAILS_URL: str = f"{GOLD_APPLE_API_URL}/catalog/product-card/base"

DEFAULT_MAX_PAGES: int = 5

DEFAULT_TIMEOUT: int = 5
TEMP_FILE: str = "products_temp.json"

PROXY_SCRAPER_TIME_OUT: int = 60
SCRAPER_API_KEY: str = config("SCRAPER_API_KEY", cast=str)
SCRAPER_API_TIME_OUT: int = 90
