import asyncio
from typing import Dict, Any, Optional
import aiohttp
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

from src.logger import get_logger

logger = get_logger("WBClient")

class WBClientError(Exception):
    """Base exception for Wildberries API client errors."""
    pass

class WBClient:
    """Asynchronous client for interacting with Wildberries API."""
    
    def __init__(self, timeout: int = 15):
        self.timeout = aiohttp.ClientTimeout(total=timeout)
        self.session: Optional[aiohttp.ClientSession] = None
        # Common headers to mimic a browser and avoid basic blocks
        self.headers = {
            "Accept": "*/*",
            "Accept-Language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7",
            "Connection": "keep-alive",
            "Origin": "https://www.wildberries.ru",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "cross-site",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
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

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((aiohttp.ClientError, asyncio.TimeoutError)),
        reraise=True
    )
    async def get(self, url: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Make a GET request to the given URL with retries on failure.
        """
        if not self.session:
            raise RuntimeError("Client session is not initialized. Use 'async with WBClient() as client:'")
            
        logger.debug(f"Fetching {url} with params {params}")
        
        try:
            async with self.session.get(url, params=params) as response:
                response.raise_for_status()
                data = await response.json(content_type=None)
                return data
        except aiohttp.ClientResponseError as e:
            logger.error(f"HTTP Error {e.status} for url {url}: {e.message}")
            raise WBClientError(f"HTTP Error {e.status}: {e.message}") from e
        except Exception as e:
            logger.error(f"Request failed for {url}: {str(e)}")
            raise
