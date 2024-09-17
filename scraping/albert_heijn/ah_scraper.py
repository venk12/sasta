import pandas as pd
import requests
from bs4 import BeautifulSoup

def scrape_products():

  categories = {
    "Aardappel, groente, fruit": "https://www.ah.nl/producten/aardappel-groente-fruit",
    "Salades, pizza, maaltijden": "https://www.ah.nl/producten/salades-pizza-maaltijden",
    "Vlees, vis": "https://www.ah.nl/producten/vlees-vis",
    "Vegetarisch, vegan en plantaardig": "https://www.ah.nl/producten/vegetarisch-vegan-en-plantaardig",
    "Kaas, vleeswaren, tapas": "https://www.ah.nl/producten/kaas-vleeswaren-tapas",
    "Zuivel, eieren, boter": "https://www.ah.nl/producten/zuivel-eieren-boter",
    "Bakkerij": "https://www.ah.nl/producten/bakkerij",
    "Ontbijtgranen en beleg": "https://www.ah.nl/producten/ontbijtgranen-en-beleg",
    "Chips, noten, toast, popcorn": "https://www.ah.nl/producten/chips-noten-toast-popcorn",
    "Snoep, chocolade, koek": "https://www.ah.nl/producten/snoep-chocolade-koek",
    "Tussendoortjes": "https://www.ah.nl/producten/tussendoortjes",
    "Koffie, thee": "https://www.ah.nl/producten/koffie-thee",
    "Frisdrank, sappen, siropen, water": "https://www.ah.nl/producten/frisdrank-sappen-siropen-water",
    "Wijn en bubbels": "https://www.ah.nl/producten/wijn-en-bubbels",
    "Bier en aperitieven": "https://www.ah.nl/producten/bier-en-aperitieven",
    "Pasta, rijst en wereldkeuken": "https://www.ah.nl/producten/pasta-rijst-en-wereldkeuken",
    "Soepen, sauzen, kruiden, olie": "https://www.ah.nl/producten/soepen-sauzen-kruiden-olie",
    "Diepvries": "https://www.ah.nl/producten/diepvries",
    "Drogisterij": "https://www.ah.nl/producten/drogisterij",
    "Gezondheid, sport": "https://www.ah.nl/producten/gezondheid-sport",
    "Baby en kind": "https://www.ah.nl/producten/baby-en-kind",
    "Huishouden": "https://www.ah.nl/producten/huishouden",
    "Huisdier": "https://www.ah.nl/producten/huisdier",
    "Koken, tafelen, vrije tijd": "https://www.ah.nl/producten/koken-tafelen-vrije-tijd"
  }

  headers = {
      'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36'
  }

  page_number = 0

  # Flag to control the loop
  continue_scraping = True

  # Initialize an empty list to collect data
  data = []

  while continue_scraping:
    for category_name, category_link in categories.items():
        print("Scraping: ", category_name, "Page Number: ", page_number)
        url = f"{category_link}?page={page_number}"
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.content, 'html.parser')

        product_containers = soup.find_all('article', class_='product-card-portrait_root__ZiRpZ product-grid-lane_gridItems__BBa4h')

        if not product_containers:
            print(f"No more products found on page {page_number} for category {category_name}. Finished scraping category.")
            continue_scraping = False
            break
        
        else:
            # Iterate over each product container and extract the required information
            for product in product_containers:
                # Extract the product name
                product_name = product.find('div', class_='product-card-portrait_content__DQ9nP').get_text(strip=True)
                product_link = product.find('a', class_='link_root__EqRHd product-card-portrait_link__5VsEK').get('href')
                product_price_int = product.find('span', class_='price-amount_integer__+e2XO').get_text(strip=True)
                product_price_decimal = product.find('span', class_='price-amount_fractional__kjJ7u').get_text(strip=True)
                product_quantity = product.find("span", class_='price_unitSize__Hk6E4').get_text(strip=True)

                # Construct the full product link
                full_product_link = f"https://www.ah.nl{product_link}"

                # Combine integer and decimal parts of the price
                product_price = f"{product_price_int}.{product_price_decimal}"

                # Append the data to the list
                data.append({
                    'product_category': category_name,
                    'product_name': product_name,
                    'product_link': full_product_link,
                    'product_price': product_price,
                    'product_quantity': product_quantity
                })
    
    page_number += 1

  df = pd.DataFrame(data)
  df = df.reindex(columns=['product_category', 'product_name', 'product_link', 'product_price', 'product_quantity'])
  return df.drop_duplicates()