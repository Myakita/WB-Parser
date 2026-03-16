# main.py
import asyncio
from client import WBClient, logger

async def main():
    client = WBClient()
    
    # Список артикулов для теста
    articles_to_parse = [146972803, 211695530, 161081548, 1111111111] # Последний — заведомо несуществующий
    
    logger.info("Начинаем сбор данных...")
    
    # Создаем задачи для параллельного выполнения
    tasks = [client.fetch_item_data(article) for article in articles_to_parse]
    
    # Запускаем все запросы (пока без ограничителя скорости для теста)
    results = await asyncio.gather(*tasks)
    
    # Фильтруем успешные результаты и выводим
    valid_items = [item for item in results if item is not None]
    
    for item in valid_items:
        print(f"[{item.article}] {item.brand} - {item.name} | Цена: {item.price} руб. | Отзывов: {item.feedbacks}")

    await client.close()
    logger.info("Работа завершена.")

if __name__ == "__main__":
    asyncio.run(main())