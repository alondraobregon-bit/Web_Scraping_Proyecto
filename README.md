# SpiderMarketplace

Proyecto de Web Scraping construido con Python y [Scrapy](https://scrapy.org/), disenado para extraer datos detallados de productos y precios del sitio de e-commerce de Falabella Peru.

## Integrantes
- Alondra Solange Obregon Carhuavilca
- Axel Roberth Portal Ruiz
- Danna Nickol Gala Vasquez
- Gerald Marcelo Fernando Borjas Bernaola

## Requisitos Previos

- Python 3.10 o superior

## Instalacion

1. Clonar el repositorio:
   ```bash
   git clone https://github.com/alondraobregon-bit/Web_Scraping_Proyecto.git
   cd Web_Scraping_Proyecto
   ```

2. Crear y activar un entorno virtual:
   ```bash
   python -m venv .venv
   ```
   - En **Windows**:
     ```bash
     .venv\Scripts\activate
     ```
   - En **macOS / Linux**:
     ```bash
     source .venv/bin/activate
     ```

3. Instalar las dependencias:
   ```bash
   pip install -r requirements.txt
   ```
   > Si no existe un archivo `requirements.txt`, instalar manualmente:
   > ```bash
   > pip install scrapy psycopg[binary] python-dotenv scrapy-rotating-proxies
   > ```

## Configuracion del Entorno

Este proyecto requiere (opcionalmente) una conexion a base de datos remota.

1. Crear un archivo `.env` en el directorio raiz del proyecto.
2. Agregar la URL de tu base de datos Supabase:

```env
SUPABASE_DB_URL=postgresql://postgres:[TU-PASSWORD]@db.[TU-REF-SUPABASE].supabase.co:5432/postgres
```

Para habilitar o deshabilitar los pipelines de limpieza y carga a BD, editar `settings.py`.

## Uso

Ejecutar el spider de **Falabella** desde el directorio raiz:

```bash
scrapy crawl falabella
```

Para exportar los datos a un archivo CSV:

```bash
scrapy crawl falabella -o falabella.csv
```

## Arquitectura de Datos

El proyecto extrae datos en un dataclass tipado `MarketplaceItem` con los siguientes campos:

### Diccionario de Datos

| Columna | Tipo | Descripcion |
|---|---|---|
| `product` | `str` | Nombre completo del producto tal como aparece en la tarjeta de Falabella. |
| `brand` | `str` | Marca del producto (ej. APPLE, SAMSUNG, XIAOMI). |
| `category` | `str` | Categoria de la URL fuente: `phones`, `laptops` o `tvs`. |
| `seller` | `str` | Nombre del vendedor en el marketplace (ej. "FALABELLA", "MARKETCELLPERU"). Se elimina el prefijo "Por" automaticamente. |
| `regular_price` | `float` | **Precio de lista / referencial** -- el precio mas alto, mostrado tachado en la tarjeta. Corresponde al atributo HTML `data-normal-price`. |
| `special_price` | `float` | **Precio con descuento general** -- precio intermedio disponible para todos los compradores. Se muestra en texto gris/negro. Corresponde al atributo HTML `data-internet-price` o `data-event-price`. |
| `cmr_price` | `float` | **Precio exclusivo CMR** -- precio mas bajo, disponible solo con tarjeta CMR Falabella / Banco Falabella. Se muestra en rojo con el badge CMR. Corresponde al atributo HTML `data-cmr-price`. |
| `rating` | `float` | Calificacion promedio del producto (escala 1.0 - 5.0), extraida del atributo `data-rating`. `None` si el producto no tiene resenas. |

### Jerarquia de Precios de Falabella

Falabella muestra hasta **3 niveles de precio** en cada tarjeta de producto, de mayor a menor:

```
+---------------------------------------------------------+
|  S/ 5,999   <- regular_price  (tachado, gris claro)     |
|  S/ 5,699   <- special_price  (texto normal, negro)     |
|  S/ 5,499   <- cmr_price      (rojo, badge CMR)         |
+---------------------------------------------------------+
```

**Casos posibles segun el producto:**

| Escenario | `regular_price` | `special_price` | `cmr_price` |
|---|---|---|---|
| 3 precios (descuento + CMR) | Tachado | Descuento general | CMR |
| 2 precios (descuento, sin CMR) | Tachado | Descuento general | `None` |
| 2 precios (solo CMR, sin intermedio) | Tachado | `None` | CMR |
| 1 precio (sin descuento) | Precio unico | `None` | `None` |

### Pipelines

Los datos pasan por dos pipelines antes de ser almacenados:

1. **CleaningPipeline**: Limpia las cadenas de texto, elimina comas/espacios y convierte los valores a representacion numerica (precios a `float`, rating a `float`).
2. **SupabasePipeline**: Abre una conexion a PostgreSQL y ejecuta operaciones `INSERT` al finalizar la ejecucion del spider.

Para habilitar o deshabilitar los pipelines, editar `settings.py`.
