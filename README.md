# SpiderMarketplace

A Web Scraping project built with Python and [Scrapy](https://scrapy.org/), designed to extract detailed product and pricing data from retail e-commerce sites (Falabella).

## Integrantes:
- Alondra Solange Obregon Carhuavilca
- Axel Roberth Portal Ruiz
- Danna Nickol Gala Vasquez
- Gerald Marcelo Fernando Borjas Bernaola

## Prerequisites

- Python 3.10 or higher.
- `uv`  

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/gmborjasb/SpiderMarketplace.git
   cd SpiderMarketplace
   ```

2. Install the dependencies and sync the environment:
   ```bash
   uv sync
   ```

## Environment Setup 

This project requires(optional) a remote database connection to operate. 

1. Create a `.env` file in the root directory of the project.
2. Add your Supabase Database URL to the file:

```env
SUPABASE_DB_URL=postgresql://postgres:[YOUR-PASSWORD]@db.[YOUR-SUPABASE-REF].supabase.co:5432/postgres
```

For enable or disable use `settings.py`

## Usage

To run the spiders, simply use the standard Scrapy CLI commands from the root directory.

Run the **Falabella** spider:
```bash
scrapy crawl falabella
```
 or 
```bash
uv run scrapy crawl falabella
```
 or
```bash
scrapy crawl falabella -o falabella.csv
```
to export data to `.csv`
 


## Data Architecture

The project extracts data into a strongly typed `MarketplaceItem` dataclass, containing the following fields:
- `product`: Product name/title.
- `brand`: Product brand.
- `category`: Category of the product. 
- `seller`: Marketplace seller name.
- `old_price`: Original crossed-out price (Decimal).
- `regular_price`: Standard price (Decimal).
- `special_price`: Discounted/Card-exclusive price (Decimal).

### Pipelines
Data flows through two main pipelines before completion:
1. **CleaningPipeline**: Cleans the raw strings, removes commas/spaces, and converts strings to numeric representations.
2. **SupabasePipeline**: Opens a connection to Postgres and performs `INSERT` operations at the end of the spider's run.

For enable or disable use `settings.py`
