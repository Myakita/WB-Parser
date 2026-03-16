# client.py
import asyncio
from curl_cffi.requests import AsyncSession
from tenacity import retry, wait_exponential, stop_after_attempt, retry_if_exception_type
from models import WBItem
import config
import logging

# Настраиваем простейший логгер
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

class RateLimitError(Exception):
    """Собственное исключение для ошибки 429"""
    pass

class WBClient:
    def __init__(self):
        # impersonate="chrome120" — главная фишка, имитируем отпечатки Chrome
        self.session = AsyncSession(impersonate="chrome120", headers={"User-Agent": config.USER_AGENT})

    async def close(self):
        await self.session.close()

    # Магия tenacity: если ловим RateLimitError, ждем (2, 4, 8... сек) и пробуем снова
    @retry(
        retry=retry_if_exception_type(RateLimitError),
        wait=wait_exponential(multiplier=1, min=config.RETRY_MIN_WAIT, max=config.RETRY_MAX_WAIT),
        stop=stop_after_attempt(config.MAX_ATTEMPTS),
        reraise=True
    )
    async def fetch_item_data(self, article: int) -> WBItem | None:
        url = f"https://card.wb.ru/cards/v1/detail?nm={article}"
        
        try:
            response = await self.session.get(url)
            
            # Перехватываем 429 и выбрасываем исключение, чтобы tenacity включил паузу
            if response.status_code == 429:
                logger.warning(f"Артикул {article}: Поймали 429! Уходим в спячку...")
                raise RateLimitError("Too Many Requests")
                
            response.raise_for_status() # Проверка других ошибок (404, 500)
            
            data = response.json()
            
            # Проверяем, есть ли товар в ответе
            if "data" in data and "products" in data["data"] and len(data["data"]["products"]) > 0:
                raw_product = data["data"]["products"][0]
                
                # Парсим через Pydantic
                item = WBItem(**raw_product)
                
                # WB отдает базовую цену с двумя лишними нулями (например, 150000 = 1500 руб)
                if "sizes" in raw_product and raw_product["sizes"]:
                    price_data = raw_product["sizes"][0].get("price")
                    if price_data and "total" in price_data:
                         item.price = int(price_data["total"] / 100)
                
                return item
            return None

        except RateLimitError:
            raise # Передаем выше для tenacity
        except Exception as e:
            logger.error(f"Ошибка при парсинге {article}: {e}")
            return None