import asyncio
from curl_cffi.requests import AsyncSession
from models import WBItem
import config
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

class WBClient:
    def __init__(self):
        # На CDN можно не притворяться браузером так жестко, но оставим для надежности
        self.session = AsyncSession(impersonate="chrome120", headers={"User-Agent": config.USER_AGENT})

    async def close(self):
        await self.session.close()

    async def _check_basket(self, url: str, basket_num: int) -> dict | None:
        """Делает быстрый запрос к одной конкретной корзине"""
        try:
            response = await self.session.get(url, timeout=3)
            if response.status_code == 200:
                logger.debug(f"Успех! Товар найден в корзине basket-{basket_num:02d}")
                return response.json()
        except Exception:
            pass
        return None

    async def fetch_item_data(self, article: int) -> WBItem | None:
        vol = article // 100000
        part = article // 1000
        
        tasks = []
        # Генерируем ссылки для всех 35 возможных серверов WB
        for i in range(1, 36):
            url = f"https://basket-{i:02d}.wbbasket.ru/vol{vol}/part{part}/{article}/info/ru/card.json"
            # Запускаем проверку
            tasks.append(self._check_basket(url, i))
            
        # asyncio.as_completed возвращает результат ТОЙ корутины, которая завершилась первой
        # Это магия: мы не ждем все 35, мы берем первый успешный ответ и идем дальше
        data = None
        for task in asyncio.as_completed(tasks):
            result = await task
            if result is not None:
                data = result
                break # Нашли данные, прерываем остальные проверки!
                
        if not data:
            logger.info(f"Артикул {article}: Не найден ни в одной из 35 корзин (404 везде).")
            return None
            
        try:
            # Парсим найденные данные
            item = WBItem(
                id=data.get("nm_id", article),
                name=data.get("imt_name", "Без названия"),
                brand=data.get("selling", {}).get("brand_name", "Неизвестный бренд"),
                price=None, # Цену из статики мы не достанем
                reviewRating=0.0,
                feedbacks=0
            )
            return item
        except Exception as e:
            logger.error(f"Ошибка при парсинге JSON для {article}: {e}")
            return None