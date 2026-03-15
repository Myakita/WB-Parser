import sqlite3
from pathlib import Path
from typing import List

from src.models import ProductCard
from src.logger import get_logger

logger = get_logger("WBDatabase")

class DBManager:
    """Менеджер для работы с базой данных SQLite"""
    
    def __init__(self, db_path: str = "data/products.db"):
        self.db_path = Path(db_path)
        self._ensure_db_folder()
        self._init_db()
        
    def _ensure_db_folder(self):
        """Создает папку для БД, если она не существует"""
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
    def _get_create_table_query(self) -> str:
        """Возвращает SQL запрос для создания таблицы"""
        return '''
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
        '''
        
    def _init_db(self):
        """Создает таблицы в базе данных"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(self._get_create_table_query())
                conn.commit()
                logger.debug("База данных успешно инициализирована.")
        except Exception as e:
            logger.error(f"Ошибка при создании БД: {e}")

    def _prepare_product_tuples(self, products: List[ProductCard]) -> list[tuple]:
        """Обертывает данные товаров в кортежи для SQL запроса"""
        return [
            (
                p.id, p.name, p.brand, p.price_rub, p.sale_price_rub,
                p.supplier, p.supplierId, p.rating, p.feedbacks
            ) for p in products
        ]

    def save_products(self, products: List[ProductCard]):
        """Обрабатывает и сохраняет список товаров в базу данных"""
        if not products:
            return
            
        try:
            data_tuples = self._prepare_product_tuples(products)
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                # Используем REPLACE для обновления существующих записей
                cursor.executemany('''
                    INSERT OR REPLACE INTO products 
                    (id, name, brand, price_rub, sale_price_rub, supplier, supplier_id, rating, feedbacks)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', data_tuples)
                
                conn.commit()
                logger.info(f"Успешно сохранено {len(products)} товаров в БД {self.db_path}")
        except Exception as e:
            logger.error(f"Ошибка при сохранении товаров в БД: {e}")
