import scrapy
import re

from Marketplace.items import MarketplaceItem


class FalabellaSpider(scrapy.Spider):
    name = "falabella"
    allowed_domains = ["falabella.com.pe"]
    custom_urls = [
        {
            "url": "https://www.falabella.com.pe/falabella-pe/category/cat760706/Celulares-y-Telefonos",
            "category": "phones",
            "last_page": 11,  # default : 170
        },
        {
            "url": "https://www.falabella.com.pe/falabella-pe/category/cat40712/Laptops",
            "category": "laptops",
            "last_page": 11,  # default : 200
        },
        {
            "url": "https://www.falabella.com.pe/falabella-pe/category/cat210477/TV-Televisores",
            "category": "tvs",
            "last_page": 11,  # default : 200
        },
    ]

    async def start(self):
        for url_dict in self.custom_urls:
            start_url = url_dict["url"]
            category = url_dict["category"]
            last_page = url_dict["last_page"]

            base_url = start_url + "?page={}"

            urls = [base_url.format(idx) for idx in range(1, last_page + 1)]

            for url in urls:
                yield scrapy.Request(
                    url=url, callback=self.parse, meta={"category": category}
                )

    def parse(self, response):
        items = response.css("div.grid-pod")

        for item in items:
            marketplaceItem = MarketplaceItem()

            category = response.meta.get("category")

            marketplaceItem.category = category

            detail = item.css("div.pod-details")

            if not detail:
                continue

            brand = detail.css("b.pod-title::text").get()
            product = detail.css("b.pod-subTitle::text").get()
            seller = detail.css("b.pod-sellerText::text").get()

            marketplaceItem.brand = brand
            marketplaceItem.product = product
            marketplaceItem.seller = seller

            prices = item.css("ol.pod-prices")

            if not prices:
                yield marketplaceItem
                continue

            regular_price = prices.css(
                "li[data-normal-price]::attr(data-normal-price)"
            ).get()
            special_price = prices.css(
                "li[data-event-price]::attr(data-event-price)"
            ).get()
            cmr_price = prices.css("li[data-cmr-price]::attr(data-cmr-price)").get()

            marketplaceItem.regular_price = regular_price
            marketplaceItem.special_price = special_price
            marketplaceItem.cmr_price = cmr_price

            yield marketplaceItem

    # Cleaning methods
    def _clean_price(self, value):
        if not value:
            return None

        value = value.replace(",", "").strip()

        return value if value else None

    def _clean_seller(self, value):
        if not value:
            return None

        value = value.strip()

        if value.upper().startswith("POR "):
            value = value[4:].strip()

        value = value.upper()

        return value

    def _clean_product(self, value):
        if not value:
            return None

        value = value.upper()

        return value
