import csv
from pathlib import Path
from typing import List

from src.models import ProductCard
from src.logger import get_logger

logger = get_logger("WBExporter")

def _get_csv_headers(products: List[ProductCard]) -> list[str]:
    """Получает заголовки колонок из первой модели товара"""
    headers = list(products[0].model_dump().keys())
    headers.extend(["price_rub", "sale_price_rub"])
    return headers

def _write_csv_rows(filepath: Path, headers: list[str], products: List[ProductCard]):
    """Записывает строки с данными товаров в CSV файл"""
    with open(filepath, mode="w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()
        
        for product in products:
            row = product.model_dump()
            row["price_rub"] = product.price_rub
            row["sale_price_rub"] = product.sale_price_rub
            writer.writerow(row)

def save_to_csv(products: List[ProductCard], filename: str = "data/results.csv"):
    """
    Основная логика: сохраняет список товаров в файл CSV.
    """
    if not products:
        logger.warning("Нет товаров для сохранения в CSV.")
        return

    # Создаем папку, если ее нет
    filepath = Path(filename)
    filepath.parent.mkdir(parents=True, exist_ok=True)
    
    headers = _get_csv_headers(products)
    
    try:
        _write_csv_rows(filepath, headers, products)
        logger.info(f"Успешно сохранено {len(products)} товаров в {filepath}")
    except Exception as e:
        logger.error(f"Ошибка при сохранении CSV {filepath}: {e}")
