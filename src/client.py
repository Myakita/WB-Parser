import asyncio
from typing import Dict, Any, Optional
import aiohttp
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

from src.logger import get_logger

logger = get_logger("WBClient")

class WBClientError(Exception):
    """Базовое исключение для ошибок клиента Wildberries."""
    pass

class WBClient:
    """Асинхронный HTTP-клиент для взаимодействия с API Wildberries."""
    
    def __init__(self, timeout: int = 15):
        self.timeout = aiohttp.ClientTimeout(total=timeout)
        self.session: Optional[aiohttp.ClientSession] = None
        # Заголовки для имитации браузера
        self.headers = {
            "Accept": "*/*",
            "Accept-Language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7",
            "Connection": "keep-alive",
            "Origin": "https://www.wildberries.ru",
            "Referer": "https://www.wildberries.ru/",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "cross-site",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36",
        }

    async def __aenter__(self):
        self.session = aiohttp.ClientSession(
            timeout=self.timeout,
            headers=self.headers
        )
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()

    def _check_session(self):
        """Проверяет, инициализирована ли сессия."""
        if not self.session:
            raise RuntimeError("Сессия не инициализирована. Используйте 'async with WBClient() as client:'")

    async def _fetch_json(self, url: str, params: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Выполняет запрос и возвращает JSON ответ."""
        async with self.session.get(url, params=params) as response:
            response.raise_for_status()
            # Разрешаем любой тип контента (API WB может вернуть text/plain)
            return await response.json(content_type=None)

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((aiohttp.ClientError, asyncio.TimeoutError)),
        reraise=True
    )
    async def get(self, url: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Выполняет GET запрос по URL с автоматическим повторением при ошибках.
        """
        self._check_session()
        logger.debug(f"Запрос к {url} с параметрами {params}")
        
        try:
            return await self._fetch_json(url, params)
        except aiohttp.ClientResponseError as e:
            logger.error(f"HTTP Ошибка {e.status} для URL {url}: {e.message}")
            raise WBClientError(f"HTTP Ошибка {e.status}: {e.message}") from e
        except Exception as e:
            logger.error(f"Ошибка запроса к {url}: {str(e)}")
            raise
