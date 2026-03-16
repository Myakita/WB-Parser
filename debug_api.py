import asyncio
import aiohttp
import json

async def debug_search():
    headers = {
        "Accept": "*/*",
        "Accept-Language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7",
        "Connection": "keep-alive",
        "Origin": "https://www.wildberries.ru",
        "Referer": "https://www.wildberries.ru/",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36",
    }
    params = {
        "ab_info": "old_bg",
        "appType": "1",
        "curr": "rub",
        "dest": "-1257786",
        "page": "1",
        "query": "кроссовки",
        "resultset": "catalog",
        "sort": "popular",
        "spp": "30",
        "suppressSpellcheck": "false",
    }
    url = "https://search.wb.ru/exactmatch/ru/common/v6/search"
    
    async with aiohttp.ClientSession(headers=headers) as session:
        async with session.get(url, params=params) as resp:
            print(f"Status: {resp.status}")
            data = await resp.json(content_type=None)
            print("Keys in response:", data.keys())
            if "data" in data:
                print("Keys in 'data':", data["data"].keys())
                if "products" in data["data"]:
                    print("Count of products:", len(data["data"]["products"]))
                    if len(data["data"]["products"]) > 0:
                        print("First product sample:", json.dumps(data["data"]["products"][0], indent=2, ensure_ascii=False))
            else:
                print("FULL RESPONSE:", json.dumps(data, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    asyncio.run(debug_search())
