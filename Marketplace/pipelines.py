# Define aquí tus pipelines de items
#
# No olvides añadir tu pipeline a la configuración ITEM_PIPELINES
# Ver: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# útil para manejar diferentes tipos de items con una única interfaz
import os
import psycopg
from dotenv import load_dotenv

load_dotenv()


class CleaningPipeline:
    def process_item(self, item, spider):
        # La limpieza de precios y vendedores ya se realiza en el spider,
        # pero mantenemos este pipeline en caso se requiera manipulación adicional.
        
        if hasattr(spider, "_clean_product"):
            item.product = spider._clean_product(item.product)

        return item


class SupabasePipeline:
    def open_spider(self, spider):
        db_url = os.getenv("SUPABASE_DB_URL")

        if not db_url:
            raise ValueError(
                "ValueError: La variable de entorno SUPABASE_DB_URL no está configurada."
            )

        self.conn = psycopg.connect(db_url)
        self.cursor = self.conn.cursor()

        self.cursor.execute(
            """
            CREATE TABLE IF not EXISTS marketplace (
                product TEXT,
                brand VARCHAR(50),
                category VARCHAR(50),
                seller VARCHAR(100),
                regular_price DECIMAL,
                special_price DECIMAL,
                has_cmr_discount INTEGER,
                scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )

        self.conn.commit()

    def process_item(self, item, spider):
        if not self.conn:
            return item

        self.cursor.execute(
            "INSERT INTO marketplace (product, brand, category, seller, regular_price, special_price, has_cmr_discount) VALUES (%s, %s, %s, %s, %s, %s, %s)",
            (
                item.product,
                item.brand,
                item.category,
                item.seller,
                item.regular_price,
                item.special_price,
                item.has_cmr_discount,
            ),
        )

        return item

    def close_spider(self, spider):
        if self.conn:
            self.conn.commit()
            self.cursor.close()
            self.conn.close()
