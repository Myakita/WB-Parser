import asyncio
import argparse
import sys

from src.client import WBClient
from src.parser import WBParser
from src.exporters import save_to_csv
from src.db import DBManager
from src.logger import get_logger

logger = get_logger("Main")

async def async_main(query: str, pages: int, export_csv: bool, export_db: bool, is_category: bool = False):
    logger.info("Initializing WB Parser...")
    
    async with WBClient() as client:
        parser = WBParser(client)
        
        try:
            if is_category:
                products = await parser.get_category_products(int(query), max_pages=pages)
            else:
                products = await parser.search_products(query, max_pages=pages)
            
            if not products:
                logger.warning("Товары не найдены. Если поиск блокируется, попробуйте режим категории (--category).")
                return
                
            if export_csv:
                save_to_csv(products)
                
            if export_db:
                db = DBManager()
                db.save_products(products)
                
            logger.info("Parsing completed successfully.")
            
        except Exception as e:
            logger.error(f"Critical error during parsing: {e}")
            sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description="Wildberries Async Parser")
    parser.add_argument("query", type=str, help="Search query (e.g., 'кроссовки')")
    parser.add_argument("-p", "--pages", type=int, default=1, help="Number of pages to parse (default: 1)")
    parser.add_argument("--no-csv", action="store_true", help="Disable CSV export")
    parser.add_argument("--no-db", action="store_true", help="Disable SQLite export")
    parser.add_argument("--category", "-c", action="store_true", help="Использовать запрос как ID категории (для обхода 429)")
    
    args = parser.parse_args()
    
    # Enable exports by default, disable if flag is passed
    export_csv = not args.no_csv
    export_db = not args.no_db
    
    try:
        # Run the async event loop
        asyncio.run(async_main(args.query, args.pages, export_csv, export_db, args.category))
    except KeyboardInterrupt:
        logger.info("Parser stopped by user.")

if __name__ == "__main__":
    main()
