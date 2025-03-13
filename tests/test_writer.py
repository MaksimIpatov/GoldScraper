import os

from scraper.utils.writer import CSVWriter


def test_writer_init():
    """Тест инициализации CSVWriter."""
    writer = CSVWriter(filename="test.csv")
    assert writer.filename == "test.csv"
    assert isinstance(writer.HEADERS, dict)


def test_save_temp(tmp_path):
    """Тест сохранения временного файла."""
    writer = CSVWriter(filename="test.csv")
    products = [{"link": "http://test.com", "name": "Test"}]
    writer.save_temp(products)

    with open("products_temp.json", "r", encoding="UTF-8") as f:
        data = f.read()
    assert "http://test.com" in data
    os.remove("products_temp.json")


def test_load_temp(tmp_path):
    """Тест загрузки временного файла."""
    writer = CSVWriter(filename="test.csv")
    products = [{"link": "http://test2.com", "name": "Test2"}]
    writer.save_temp(products)

    loaded = writer.load_temp()
    assert loaded[0]["link"] == "http://test2.com"
    os.remove("products_temp.json")


def test_write(tmp_path):
    """Тест записи в CSV."""
    writer = CSVWriter(filename=os.path.join(tmp_path, "test.csv"))
    products = [
        {"link": "http://test.com", "name": "Test", "price": "100"},
        {"link": "http://test2.com", "name": "Test2"},
    ]
    writer.write(products)

    with open(tmp_path / "test.csv", "r", encoding="UTF-8") as f:
        content = f.read()
    assert "http://test.com" in content
    assert "100" in content
    assert "N/A" in content
    assert not os.path.exists("products_temp.json")
