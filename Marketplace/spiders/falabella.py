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
            "last_page": 13,
        },
        {
            "url": "https://www.falabella.com.pe/falabella-pe/category/cat40712/Laptops",
            "category": "laptops",
            "last_page": 13,
        },
        {
            "url": "https://www.falabella.com.pe/falabella-pe/category/cat210477/TV-Televisores",
            "category": "tvs",
            "last_page": 13,
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
            marketplace_item = MarketplaceItem()

            category = response.meta.get("category")
            marketplace_item.category = category

            detail = item.css("div.pod-details")

            if not detail:
                continue

            brand = detail.css("b.pod-title::text").get()
            product = detail.css("b.pod-subTitle::text").get()
            seller = detail.css("b.pod-sellerText::text").get()

            marketplace_item.brand = brand
            marketplace_item.product = product
            marketplace_item.seller = self._clean_seller(seller)

            # --- Extract prices (already cleaned to float) ---
            regular_price, special_price, cmr_price = self._extract_prices(item)
            marketplace_item.regular_price = regular_price
            marketplace_item.special_price = special_price
            marketplace_item.cmr_price = cmr_price

            # --- Extract rating (already cleaned to float) ---
            marketplace_item.rating = self._extract_rating(item)

            yield marketplace_item

    # ------------------------------------------------------------------ #
    #                       Price extraction                              #
    # ------------------------------------------------------------------ #

    def _extract_prices(self, card):
        """Extract regular_price, special_price and cmr_price from a product card.

        Falabella uses four possible data-attributes on ``<li>`` elements
        inside ``ol.pod-prices``:

        * ``data-normal-price``   -- list / reference price (shown struck-through)
        * ``data-internet-price`` -- online discount price (grey/black text)
        * ``data-event-price``    -- promotional / event price (grey/black text)
        * ``data-cmr-price``      -- exclusive CMR Falabella card price (red text)

        Mapping rules:
        * ``regular_price``  <- ``data-normal-price`` (the highest, struck-through)
        * ``special_price``  <- ``data-internet-price`` OR ``data-event-price``
          (whichever is present; they are mutually exclusive in practice)
        * ``cmr_price``      <- ``data-cmr-price``

        Returns float values with thousand-separator commas removed.
        """
        prices_ol = card.css("ol.pod-prices")

        if not prices_ol:
            return None, None, None

        regular_price = prices_ol.css(
            "li[data-normal-price]::attr(data-normal-price)"
        ).get()

        # The intermediate discount price can appear under two different
        # attribute names depending on how Falabella categorises the offer.
        special_price = prices_ol.css(
            "li[data-internet-price]::attr(data-internet-price)"
        ).get()
        if special_price is None:
            special_price = prices_ol.css(
                "li[data-event-price]::attr(data-event-price)"
            ).get()

        cmr_price = prices_ol.css(
            "li[data-cmr-price]::attr(data-cmr-price)"
        ).get()

        return (
            self._clean_price(regular_price),
            self._clean_price(special_price),
            self._clean_price(cmr_price),
        )

    # ------------------------------------------------------------------ #
    #                       Rating extraction                             #
    # ------------------------------------------------------------------ #

    def _extract_rating(self, card):
        """Extract the numeric rating from a product card.

        Falabella renders ratings inside a ``<div class="ratings">`` element
        with a ``data-rating`` attribute holding the average score as a float
        (e.g. ``"4.7422"``).

        Returns the value as a float rounded to 2 decimals,
        or ``None`` when no rating is available.
        """
        raw = card.css("div.ratings[data-rating]::attr(data-rating)").get()

        if raw is None:
            return None

        try:
            return round(float(raw), 2)
        except (ValueError, TypeError):
            return None

    # ------------------------------------------------------------------ #
    #                       Cleaning helpers                              #
    # ------------------------------------------------------------------ #

    def _clean_price(self, value):
        """Remove thousand-separator commas and convert to float."""
        if not value:
            return None

        value = value.replace(",", "").strip()

        if not value:
            return None

        try:
            return float(value)
        except (ValueError, TypeError):
            return None

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
