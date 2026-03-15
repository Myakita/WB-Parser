import asyncio
from typing import List, Optional
from pydantic import ValidationError

from src.client import WBClient
from src.models import ProductCard, SearchResponse
from src.logger import get_logger

logger = get_logger("WBParser")

class WBParser:
    """Main parser class for Wildberries"""
    
    SEARCH_URL = "https://search.wb.ru/exactmatch/ru/common/v4/search"
    
    def __init__(self, client: WBClient):
        self.client = client

    async def search_products(self, query: str, max_pages: int = 1) -> List[ProductCard]:
        """
        Search for products by query across multiple pages.
        """
        all_products: List[ProductCard] = []
        
        logger.info(f"Starting search for '{query}', max pages: {max_pages}")
        
        for page in range(1, max_pages + 1):
            logger.info(f"Parsing page {page} for query '{query}'")
            page_products = await self._parse_search_page(query, page)
            
            if not page_products:
                logger.info(f"No more products found on page {page}. Stopping.")
                break
                
            all_products.extend(page_products)
            
            # Polymorphic delay between page requests to avoid bans
            if page < max_pages:
                await asyncio.sleep(1)
                
        logger.info(f"Finished search. Total products found: {len(all_products)}")
        return all_products

    async def _parse_search_page(self, query: str, page: int) -> List[ProductCard]:
        """
        Parse a single page of search results.
        """
        params = {
            "query": query,
            "resultset": "catalog",
            "sort": "popular",
            "page": page,
            "suppressSpellcheck": "false",
            "dest": "-1257786" # Default Moscow destination
        }
        
        try:
            data = await self.client.get(self.SEARCH_URL, params=params)
            
            # Validate and parse using pydantic models
            response = SearchResponse.model_validate(data)
            return response.data.products
            
        except ValidationError as e:
            logger.error(f"Failed to validate response data: {e}")
            return []
        except Exception as e:
            logger.error(f"Failed to parse page {page}: {e}")
            return []
