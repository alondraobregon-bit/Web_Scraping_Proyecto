import scrapy
import re

from twisted.internet.error import DNSLookupError
from twisted.internet.error import TimeoutError, TCPTimedOutError

from Marketplace.items import MarketplaceItem


class FalabellaSpider(scrapy.Spider):
    name = "falabella"
    allowed_domains = ["falabella.com.pe"]
    custom_urls = [
        {
            "url": "https://www.falabella.com.pe/falabella-pe/category/cat760706/Celulares-y-Telefonos",
            "category": "phones",
            "last_page": 20,
        },
        {
            "url": "https://www.falabella.com.pe/falabella-pe/category/cat40712/Laptops",
            "category": "laptops",
            "last_page": 20,
        },
        {
            "url": "https://www.falabella.com.pe/falabella-pe/category/cat210477/TV-Televisores",
            "category": "tvs",
            "last_page": 20,
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
                    url=url, 
                    callback=self.parse, 
                    errback=self.errback_handler, # Manejador explícito de fallos
                    meta={"category": category}
                )

    def errback_handler(self, failure):
        """
        Manejo de errores explícito (try-except) para conexiones fallidas.
        Requisito de la rúbrica del proyecto.
        """
        self.logger.error("Se detectó un fallo en la conexión HTTP.")
        
        try:
            # failure.raiseException() lanza el error original que causó el fallo
            failure.raiseException()
        except TimeoutError:
            self.logger.error("TimeoutError: El servidor tardó demasiado en responder.")
        except TCPTimedOutError:
            self.logger.error("TCPTimedOutError: Conexión fallida por Timeout en TCP.")
        except DNSLookupError:
            self.logger.error("DNSLookupError: Fallo de red, no se pudo resolver el dominio.")
        except Exception as e:
            self.logger.error(f"Error de conexión general capturado: {e}")

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

            # --- Extraer precios ---
            regular_price, special_price, has_cmr = self._extract_prices(item)
            marketplace_item.regular_price = regular_price
            marketplace_item.special_price = special_price
            marketplace_item.has_cmr_discount = has_cmr

            yield marketplace_item

    # Extraccion de precios y evaluacion de CMR

    def _extract_prices(self, card):
        """Extrae el precio regular, precio especial y evalúa la presencia de CMR.

        Falabella utiliza cuatro posibles atributos de datos en los elementos ``<li>``
        dentro de ``ol.pod-prices``:

        * ``data-normal-price``   -- precio de lista / referencial (tachado)
        * ``data-internet-price`` -- precio con descuento online (texto gris/negro)
        * ``data-event-price``    -- precio promocional / evento (texto gris/negro)
        * ``data-cmr-price``      -- precio exclusivo con tarjeta CMR Falabella (texto rojo)

        Devuelve valores float sin comas separadoras de miles para los precios,
        y 1 o 0 para has_cmr_discount dependiendo si data-cmr-price está presente.
        """
        prices_ol = card.css("ol.pod-prices")

        if not prices_ol:
            return None, None, 0

        regular_price = prices_ol.css(
            "li[data-normal-price]::attr(data-normal-price)"
        ).get()

        # El precio con descuento intermedio puede aparecer bajo dos nombres
        # de atributos diferentes dependiendo de cómo Falabella categorice la oferta.
        special_price = prices_ol.css(
            "li[data-internet-price]::attr(data-internet-price)"
        ).get()
        if special_price is None:
            special_price = prices_ol.css(
                "li[data-event-price]::attr(data-event-price)"
            ).get()

        cmr_price_raw = prices_ol.css(
            "li[data-cmr-price]::attr(data-cmr-price)"
        ).get()

        # Determinar si existe un descuento CMR (1 = Verdadero, 0 = Falso)
        has_cmr_discount = 1 if cmr_price_raw else 0

        return (
            self._clean_price(regular_price),
            self._clean_price(special_price),
            has_cmr_discount
        )

    # Funciones de limpieza
    def _clean_price(self, value):
        """Elimina las comas separadoras de miles y convierte a float."""
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
        """Limpia el nombre del vendedor (ej. remueve el prefijo 'Por ')."""
        if not value:
            return None

        value = value.strip()

        if value.upper().startswith("POR "):
            value = value[4:].strip()

        value = value.upper()

        return value

    def _clean_product(self, value):
        """Convierte el nombre del producto a mayúsculas para mantener consistencia."""
        if not value:
            return None

        value = value.upper()

        return value
