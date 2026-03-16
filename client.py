import asyncio
from curl_cffi.requests import AsyncSession
from tenacity import retry, wait_exponential, stop_after_attempt, retry_if_exception_type
from aiolimiter import AsyncLimiter
from models import WBItem
import config
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

class RateLimitError(Exception):
    pass

class WBClient:
    def __init__(self):
        self.session = AsyncSession(impersonate="chrome120", headers={"User-Agent": config.USER_AGENT})
        self.limiter = AsyncLimiter(config.REQUESTS_PER_SECOND, 1)

    async def close(self):
        await self.session.close()

    @retry(
        retry=retry_if_exception_type(RateLimitError),
        wait=wait_exponential(multiplier=1, min=config.RETRY_MIN_WAIT, max=config.RETRY_MAX_WAIT),
        stop=stop_after_attempt(config.MAX_ATTEMPTS),
        reraise=True
    )
    async def fetch_item_data(self, article: int) -> WBItem | None:
        url = f"https://card.wb.ru/cards/v1/detail?nm={article}"
        
        async with self.limiter: 
            try:
                response = await self.session.get(url)
                
                if response.status_code == 429:
                    logger.warning(f"Артикул {article}: Поймали 429! Уходим в спячку...")
                    raise RateLimitError("Too Many Requests")
                    
                response.raise_for_status()
                
                data = response.json()
                
                if "data" in data and "products" in data["data"] and len(data["data"]["products"]) > 0:
                    raw_product = data["data"]["products"][0]
                    item = WBItem(**raw_product)
                    
                    if "sizes" in raw_product and raw_product["sizes"]:
                        price_data = raw_product["sizes"][0].get("price")
                        if price_data and "total" in price_data:
                             item.price = int(price_data["total"] / 100)
                    
                    return item
                return None

            except RateLimitError:
                raise 
            except Exception as e:
                logger.error(f"Ошибка при парсинге {article}: {e}")
                return None