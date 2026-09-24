import scrapy
import re

from Marketplace.items import MarketplaceItem


class RipleySpider(scrapy.Spider):
    name = "ripley"
    allowed_domains = ["simple.ripley.com.pe"]
    start_url = (
        "https://simple.ripley.com.pe/tecnologia/celulares/celulares-y-smartphones"
    )

    # last_page = 45
    last_page = 2

    async def start(self):
        base_url = self.start_url + "?page={}"

        urls = [base_url.format(idx) for idx in range(1, self.last_page + 1)]

        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        items = response.css("a.product-link")

        for item in items:
            data_item = item.css("article.product-item--wrapper")

            if not data_item:
                continue

            marketplaceItem = MarketplaceItem()

            marketplaceItem.seller = None

            brand = data_item.css("span.product-item--brand::text").get()
            product = data_item.css("p.product-item--name::text").get()
            prices = data_item.css("div.product-price-wrapper")

            marketplaceItem.brand = brand
            marketplaceItem.product = product

            if not prices:
                yield marketplaceItem
                continue

            old_price = prices.css("span.product-price-strikethrough::text").get()
            regular_price = prices.css(
                "span.product-price-no-strikethrough::text"
            ).get()
            special_price = prices.css("span.product-price-ripley-price::text").get()

            marketplaceItem.old_price = old_price
            marketplaceItem.regular_price = regular_price
            marketplaceItem.special_price = special_price

            yield marketplaceItem

    # Cleaning methods
    def _clean_price(self, value):
        if not value:
            return None

        value = re.sub(r"[S/,\s\xa0]", "", value).strip()

        return value if value else None

    # def _clean_seller(self, value):
    #     if not value:
    #         return None
    #
    #     value = value.upper()
    #     value = re.sub(r"POR ", "")
    #
    #     return value

    def _clean_product(self, value):
        if not value:
            return None

        value = value.upper()

        return value
