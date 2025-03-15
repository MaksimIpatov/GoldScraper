from scraper.core.headers_manager import HeadersManager


def test_headers_manager_init(mocker):
    """Тест инициализации HeadersManager."""
    mocker.patch(
        "scraper.core.headers_manager.get_cookies",
        return_value={"cookie1": "value1"},
    )
    manager = HeadersManager()
    assert isinstance(manager.headers, dict)
    assert "User-Agent" in manager.headers
    assert manager.cookies == {"cookie1": "value1"}


def test_generate_headers():
    """Тест генерации заголовков."""
    manager = HeadersManager()
    headers = manager.generate_headers()
    assert "User-Agent" in headers
    assert headers["Accept"] == "application/json, text/plain, */*"
    assert headers["Referer"] == "https://goldapple.ru/parfjumerija"


def test_get_headers_and_cookies(mocker):
    """Тест получения заголовков и кук."""
    mocker.patch(
        "scraper.core.headers_manager.get_cookies",
        return_value={"cookie2": "value2"},
    )
    manager = HeadersManager()
    headers, cookies = manager.get_headers_and_cookies()
    assert isinstance(headers, dict)
    assert isinstance(cookies, dict)
    assert cookies == {"cookie2": "value2"}


def test_update_cookies(mocker):
    """Тест обновления кук."""
    mocker.patch(
        "scraper.core.headers_manager.get_cookies",
        return_value={"new_cookie": "new_value"},
    )
    manager = HeadersManager()
    manager.update_cookies()
    assert manager.cookies == {"new_cookie": "new_value"}
