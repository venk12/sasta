import os
import requests
from bs4 import BeautifulSoup
import pandas as pd
import csv
import time


def scrape_products():
    # List of category URLs
    categories = {
        "aardappelen_groente_fruit": "https://www.jumbo.com/producten/aardappelen,-groente-en-fruit/",
        "verse_maaltijden_gemak": "https://www.jumbo.com/producten/verse-maaltijden-en-gemak/",
        "vlees_vis_en_vega": "https://www.jumbo.com/producten/vlees,-vis-en-vega/",
        "brood_en_gebak": "https://www.jumbo.com/producten/brood-en-gebak/",
        "vleeswaren_kaas_tapas": "https://www.jumbo.com/producten/vleeswaren,-kaas-en-tapas/",
        "zuivel_eieren_boter": "https://www.jumbo.com/producten/zuivel,-eieren,-boter/",
        "conserven_soepen_sauzen_olien": "https://www.jumbo.com/producten/conserven,-soepen,-sauzen,-olien/",
        "wereldkeukens_kruiden_pasta_rijst": "https://www.jumbo.com/producten/wereldkeukens,-kruiden,-pasta-en-rijst/",
        "ontbijt_broodbeleg_bakproducten": "https://www.jumbo.com/producten/ontbijt,-broodbeleg-en-bakproducten/",
        "koek_snoep_chocolade_chips": "https://www.jumbo.com/producten/koek,-snoep,-chocolade-en-chips/",
        "koffie_thee": "https://www.jumbo.com/producten/koffie-en-thee/",
        "frisdrank_sappen": "https://www.jumbo.com/producten/frisdrank-en-sappen/",
        "bier_wijn": "https://www.jumbo.com/producten/bier-en-wijn/",
        "diepvries": "https://www.jumbo.com/producten/diepvries/",
        "drogisterij": "https://www.jumbo.com/producten/drogisterij/",
        "baby_peuter": "https://www.jumbo.com/producten/baby,-peuter/",
        "huishouden_dieren_servicebalie": "https://www.jumbo.com/producten/huishouden,-dieren,-servicebalie/"
    }

    # Headers to mimic a browser request
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36'
    }

    # Initialize an empty list to store all products data
    all_products = []

    # Function to scrape a category
    def scrape_category(category_name, category_url):
        print(f"Scraping category: {category_name}")

        page = 0  # Start with the first page
        while True:
            offSet = page * 24
            print(f"Scraping page {page + 1} with offSet {offSet}...")

            # Construct the URL for the current page
            url = f"{category_url}?offSet={offSet}"

            # Send a GET request to the website
            response = requests.get(url, headers=headers)

            # Parse the content with BeautifulSoup
            soup = BeautifulSoup(response.content, 'lxml')

            # Find all product containers
            product_containers = soup.find_all('article', class_='product-container')

            # If no products found, stop further scraping for this category
            if not product_containers:
                print(f"No more products found on page {page + 1}. Finished scraping category.")
                break

            # Iterate over each product container and extract the required information
            for product in product_containers:
                # Extract the product name
                product_name_elem = product.find('h3', class_='jum-heading')
                product_name = product_name_elem.get_text(strip=True) if product_name_elem else "N/A"

                # Extract the product link
                product_link_tag = product.find('a', class_='link')
                product_link = product_link_tag['href'] if product_link_tag else "N/A"

                # Extract the product price
                product_price_whole_elem = product.find('span', class_='whole')
                product_price_fractional_elem = product.find('span', class_='fractional')
                
                if product_price_whole_elem and product_price_fractional_elem:
                    product_price_whole = product_price_whole_elem.get_text(strip=True)
                    product_price_fractional = product_price_fractional_elem.get_text(strip=True)
                    product_price = f"{product_price_whole}.{product_price_fractional} €"
                else:
                    product_price = "N/A"

                # Attempt to extract the product price per unit, if it exists
                price_per_unit_div = product.find('div', class_='price-per-unit')
                price_per_unit = price_per_unit_div.get_text(strip=True) if price_per_unit_div else "N/A"

                # Extract the quantity information
                product_quantity = price_per_unit.split('/')[1] if '/' in price_per_unit else "N/A"

                # Append the product data to the list
                all_products.append({
                    'Category': category_name,
                    'Product Name': product_name,
                    'Product Link': product_link,
                    'Price': product_price,
                    'Quantity': product_quantity
                })

            # Move to the next page
            page += 1

            # Optional: Add a short delay to avoid overloading the server (respectful scraping)
            time.sleep(0.25)

        print(f"Finished scraping category: {category_name}.")

    # Iterate over each category and scrape it
    for category_name, category_url in categories.items():
        scrape_category(category_name, category_url)

    # Convert the list of dictionaries to a DataFrame
    df = pd.DataFrame(all_products)

    # Return the DataFrame
    return df.drop_duplicates()