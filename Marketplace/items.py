# Define aquí los modelos para los items extraídos
#
# Ver documentación en:
# https://docs.scrapy.org/en/latest/topics/items.html

from dataclasses import dataclass
from typing import Optional


@dataclass
class MarketplaceItem:
    product: Optional[str] = None
    brand: Optional[str] = None
    category: Optional[str] = None
    seller: Optional[str] = None
    regular_price: Optional[float] = None
    special_price: Optional[float] = None
    has_cmr_discount: Optional[int] = None
