import sqlite3
from pathlib import Path
from typing import List

from src.models import ProductCard
from src.logger import get_logger

logger = get_logger("WBDatabase")

class DBManager:
    """Manager for SQLite database storage"""
    
    def __init__(self, db_path: str = "data/products.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()
        
    def _init_db(self):
        """Create tables if they do not exist"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS products (
                        id INTEGER PRIMARY KEY,
                        name TEXT,
                        brand TEXT,
                        price_rub REAL,
                        sale_price_rub REAL,
                        supplier TEXT,
                        supplier_id INTEGER,
                        rating INTEGER,
                        feedbacks INTEGER
                    )
                ''')
                conn.commit()
                logger.debug("Database initialized successfully.")
        except Exception as e:
            logger.error(f"Failed to initialize database: {e}")

    def save_products(self, products: List[ProductCard]):
        """Save a list of products to the database"""
        if not products:
            return
            
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Use executemany for bulk insert/update
                # We use REPLACE to update existing records with the same ID
                data = [
                    (
                        p.id,
                        p.name,
                        p.brand,
                        p.price_rub,
                        p.sale_price_rub,
                        p.supplier,
                        p.supplierId,
                        p.rating,
                        p.feedbacks
                    ) for p in products
                ]
                
                cursor.executemany('''
                    INSERT OR REPLACE INTO products 
                    (id, name, brand, price_rub, sale_price_rub, supplier, supplier_id, rating, feedbacks)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', data)
                
                conn.commit()
                logger.info(f"Successfully saved {len(products)} products to database {self.db_path}")
        except Exception as e:
            logger.error(f"Failed to save products to DB: {e}")
