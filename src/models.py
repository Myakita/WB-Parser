from typing import List, Optional
from pydantic import BaseModel, Field

class ProductCard(BaseModel):
    id: int
    name: str = Field(default="")
    brand: str = Field(default="")
    
    # Prices on WB are usually represented in kopecks (cents).
    priceU: int = Field(default=0)
    salePriceU: int = Field(default=0)
    
    supplier: str = Field(default="")
    supplierId: Optional[int] = None
    
    # Feedbacks and rating
    rating: int = Field(default=0)
    feedbacks: int = Field(default=0)
    
    @property
    def price_rub(self) -> float:
        """Convert standard price from kopecks to rubles"""
        return self.priceU / 100.0
        
    @property
    def sale_price_rub(self) -> float:
        """Convert sale price from kopecks to rubles"""
        return self.salePriceU / 100.0

class SearchData(BaseModel):
    products: List[ProductCard] = Field(default_factory=list)

class SearchResponse(BaseModel):
    state: int = Field(default=0)
    data: SearchData = Field(default_factory=SearchData)
