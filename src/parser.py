import asyncio
from typing import List, Optional
from pydantic import ValidationError

from src.client import WBClient
from src.models import ProductCard, SearchResponse
from src.logger import get_logger

logger = get_logger("WBParser")

class WBParser:
    """Главный класс парсера для Wildberries"""
    
    SEARCH_URL = "https://search.wb.ru/exactmatch/ru/common/v2/search"
    
    def __init__(self, client: WBClient):
        self.client = client

    async def search_products(self, query: str, max_pages: int = 1) -> List[ProductCard]:
        """Ищет товары по запросу проходя по нескольким страницам."""
        all_products: List[ProductCard] = []
        logger.info(f"Начинаем поиск по '{query}', максимум страниц: {max_pages}")
        
        for page in range(1, max_pages + 1):
            logger.info(f"Парсинг страницы {page}...")
            page_products = await self._parse_search_page(query, page)
            
            if not page_products:
                logger.info(f"Больше товаров на странице {page} нет. Остановка.")
                break
                
            all_products.extend(page_products)
            await self._random_delay_if_needed(page, max_pages)
                
        logger.info(f"Поиск завершен. Найдено всего товаров: {len(all_products)}")
        return all_products

    async def _random_delay_if_needed(self, current_page: int, max_pages: int):
        """Добавляет задержку между запросами."""
        if current_page < max_pages:
            await asyncio.sleep(1)

    def _get_search_params(self, query: str, page: int) -> dict:
        """Параметры для запроса поиска API"""
        return {
            "appType": "1",
            "curr": "rub",
            "dest": "-1257786",
            "page": page,
            "query": query,
            "resultset": "catalog",
            "sort": "popular",
            "spp": "30"
        }

    async def _parse_search_page(self, query: str, page: int) -> List[ProductCard]:
        """Парсит одну страницу поисковой выдачи."""
        params = self._get_search_params(query, page)
        try:
            data = await self.client.get(self.SEARCH_URL, params=params)
            return self._validate_response(data)
        except Exception as e:
            logger.error(f"Ошибка парсинга страницы {page}: {e}")
            return []

    def _validate_response(self, data: dict) -> List[ProductCard]:
        """Валидирует полученный JSON через Pydantic"""
        try:
            response = SearchResponse.model_validate(data)
            return response.data.products
        except ValidationError as e:
            logger.error(f"Ошибка валидации: {e}")
            return []
