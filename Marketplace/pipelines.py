# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
import os
import psycopg
from dotenv import load_dotenv

load_dotenv()


class CleaningPipeline:
    def process_item(self, item, spider):

        if hasattr(spider, "_clean_price"):
            reg = spider._clean_price(item.regular_price)
            spe = spider._clean_price(item.special_price)
            cmr = spider._clean_price(item.cmr_price)

            item.regular_price = float(reg) if reg else None
            item.special_price = float(spe) if spe else None
            item.cmr_price = float(cmr) if cmr else None

        if hasattr(spider, "_clean_seller"):
            item.seller = spider._clean_seller(item.seller)

        if hasattr(spider, "_clean_product"):
            item.product = spider._clean_product(item.product)

        # Rating is already cleaned by the spider; convert to float
        if item.rating is not None:
            try:
                item.rating = float(item.rating)
            except (ValueError, TypeError):
                item.rating = None

        return item


class SupabasePipeline:
    def open_spider(self, spider):
        db_url = os.getenv("SUPABASE_DB_URL")

        if not db_url:
            raise ValueError(
                "ValueError: Environment variable SUPABASE_DB_URL is not set."
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
                cmr_price DECIMAL,
                rating DECIMAL,
                scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )

        self.conn.commit()

    def process_item(self, item, spider):
        if not self.conn:
            return item

        self.cursor.execute(
            "INSERT INTO marketplace (product, brand, category, seller, regular_price, special_price, cmr_price, rating) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
            (
                item.product,
                item.brand,
                item.category,
                item.seller,
                item.regular_price,
                item.special_price,
                item.cmr_price,
                item.rating,
            ),
        )

        return item

    def close_spider(self, spider):
        if self.conn:
            self.conn.commit()
            self.cursor.close()
            self.conn.close()
