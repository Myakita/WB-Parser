# models.py
from pydantic import BaseModel, Field
from typing import Optional

class WBItem(BaseModel):
    article: int = Field(alias="id")  # WB отдает артикул в поле "id"
    name: str = Field(default="Без названия")
    brand: str = Field(default="Неизвестный бренд")
    price: Optional[int] = Field(default=None) # Цену будем считать позже (WB отдает ее умноженную на 100)
    rating: float = Field(default=0.0, alias="reviewRating")
    feedbacks: int = Field(default=0)