from src.models import ProductCard

def test_product_card_model_parsing():
    raw_data = {
        "id": 12345,
        "name": "Тестовые кроссовки",
        "brand": "Nike",
        "priceU": 500000,
        "salePriceU": 250000,
        "supplier": "TestSupplier",
        "rating": 5,
        "feedbacks": 100
    }
    
    product = ProductCard.model_validate(raw_data)
    
    assert product.id == 12345
    assert product.name == "Тестовые кроссовки"
    # Testing calculated properties (Kopecks to Rubles)
    assert product.price_rub == 5000.0
    assert product.sale_price_rub == 2500.0

def test_product_card_defaults():
    raw_data = {
        "id": 999
    }
    
    product = ProductCard.model_validate(raw_data)
    
    assert product.id == 999
    assert product.name == ""
    assert product.price_rub == 0.0
    assert product.sale_price_rub == 0.0
    assert product.rating == 0
