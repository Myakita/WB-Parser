import csv
from pathlib import Path
from typing import List

from src.models import ProductCard
from src.logger import get_logger

logger = get_logger("WBExporter")

def save_to_csv(products: List[ProductCard], filename: str = "data/results.csv"):
    """
    Save a list of ProductCard models to a CSV file.
    """
    if not products:
        logger.warning("No products to save to CSV.")
        return

    # Ensure data directory exists
    filepath = Path(filename)
    filepath.parent.mkdir(parents=True, exist_ok=True)
    
    # Extract headers from the Pydantic model
    headers = list(products[0].model_dump().keys())
    # Add our custom properties
    headers.extend(["price_rub", "sale_price_rub"])
    
    try:
        with open(filepath, mode="w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=headers)
            writer.writeheader()
            
            for product in products:
                row = product.model_dump()
                row["price_rub"] = product.price_rub
                row["sale_price_rub"] = product.sale_price_rub
                writer.writerow(row)
                
        logger.info(f"Successfully saved {len(products)} products to {filepath}")
    except Exception as e:
        logger.error(f"Failed to save CSV to {filepath}: {e}")
