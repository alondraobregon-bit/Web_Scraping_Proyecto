# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

from dataclasses import dataclass
from typing import Concatenate, Optional

import scrapy


@dataclass
class MarketplaceItem:
    product: Optional[str] = None
    brand: Optional[str] = None
    category: Optional[str] = None
    seller: Optional[str] = None
    regular_price: Optional[str] = None
    special_price: Optional[str] = None
    cmr_price: Optional[str] = None
