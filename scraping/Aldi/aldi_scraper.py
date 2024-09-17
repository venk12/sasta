import pandas as pd
from rapidfuzz import process, fuzz
import os
import requests
from bs4 import BeautifulSoup

def scrape_sub_categories(url):
    response = requests.get(url)
    response.raise_for_status()
    
    soup = BeautifulSoup(response.text, 'html.parser')
    
    sub_categories = {}
    # Find all the sub-categories by their div class
    for div in soup.find_all('div', class_="mod-content-tile__content"):
        h4_tag = div.find('h4')
        link_tag = div.find('a', class_="link link--primary")
        
        if h4_tag and link_tag:
            sub_category_name = h4_tag.text.strip()
            sub_category_link = link_tag['href']
            sub_categories[sub_category_name] = "https://www.aldi.nl" + sub_category_link

    return sub_categories


def scrape_products():
    categories = {
        'Aardappels, groente, fruit': 'https://www.aldi.nl/producten/aardappels-groente-fruit.html',
        'Brood, bakkerij': 'https://www.aldi.nl/producten/brood-bakkerij.html',
        'Ontbijtgranen, broodbeleg, tussendoortjes': 'https://www.aldi.nl/producten/ontbijtgranen-broodbeleg-tussendoortjes.html',
        'Zuivel, eieren, boter': 'https://www.aldi.nl/producten/zuivel-eieren-boter.html',
        'Kaas, vleeswaren, tapas': 'https://www.aldi.nl/producten/kaas-vleeswaren-tapas.html',
        'Wijn': 'https://www.aldi.nl/producten/wijn.html',
        'Vlees, vis, vega': 'https://www.aldi.nl/producten/vlees-vis-vega.html',
        'Maaltijden, salades': 'https://www.aldi.nl/producten/maaltijden-salades.html',
        'Pasta, rijst, bakken, internationale keuken': 'https://www.aldi.nl/producten/pasta-rijst-bakken-internationale-keuken.html',
        'Soepen, sauzen, smaakmakers, conserven': 'https://www.aldi.nl/producten/soepen-sauzen-smaakmakers-conserven.html',
        'Snoep, koeken': 'https://www.aldi.nl/producten/snoep-koeken.html',
        'Chips, noten': 'https://www.aldi.nl/producten/chips-noten.html',
        'Diepvries': 'https://www.aldi.nl/producten/diepvries.html',
        'Bier en likeuren': 'https://www.aldi.nl/producten/bier-en-likeuren.html',
        'Sappen, frisdrank': 'https://www.aldi.nl/producten/sappen-frisdrank.html',
        'Thee, koffie': 'https://www.aldi.nl/producten/thee-koffie.html',
        'Huishouden': 'https://www.aldi.nl/producten/huishouden.html',
        'Baby, persoonlijke verzorging': 'https://www.aldi.nl/producten/baby-persoonlijke-verzorging.html',
        'Huisdieren': 'https://www.aldi.nl/producten/huisdieren.html',
        'Prijsverlagingen': 'https://www.aldi.nl/producten/Prijsverlagingen.html',
        'Zomerassortiment': 'https://www.aldi.nl/producten/zomerassortiment.html',
        'Cadeaukaarten': 'https://www.aldi.nl/producten/cadeaukaarten.html'
        }

    # Initialize an empty dictionary to hold all subcategory data
    all_sub_categories = {}

    # Iterate over the main categories and collect sub-categories into a flat structure
    for category, url in categories.items():
        sub_categories = scrape_sub_categories(url)
        all_sub_categories.update(sub_categories)

    # Initialize an empty DataFrame to store the data for all categories
    df_aldi = pd.DataFrame(columns=['product_category', 'product_link', 'product_name', 'product_price', 'product_quantity'])

    # Iterate over each category and its link in all_sub_categories
    for category_name, category_link in all_sub_categories.items():
        print(f"Scraping category: {category_name} from URL: {category_link}")
        
        try:
            # Fetch the category page content
            response = requests.get(category_link)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Find all product tiles on the category page
            tiles = soup.find_all('div', class_="mod mod-article-tile-placeholder mod-article-tile-placeholder--small")
            
            # Extract the 'data-tile-url' attribute for each product
            tile_urls = ["https://www.aldi.nl/" + tile['data-tile-url'] for tile in tiles if 'data-tile-url' in tile.attrs]
            
            # Create a temporary DataFrame for the current category
            df = pd.DataFrame({
                'product_category': [category_name] * len(tile_urls),
                'product_name': [""] * len(tile_urls),
                'product_link': tile_urls,
                'product_price': [""] * len(tile_urls),
                'product_quantity': [""] * len(tile_urls)
            })
            
            # Iterate over each row in the DataFrame and scrape the data
            for index, row in df.iterrows():
                product_link = row['product_link']
                # print(f"Scraping product URL: {product_link}")
                
                try:
                    # Fetch the product page content
                    response = requests.get(product_link)
                    response.raise_for_status()  # Ensure the request was successful
                    
                    # Parse the HTML content
                    product_soup = BeautifulSoup(response.text, 'html.parser')
                    
                    # Scrape product data: price, quantity, and product name
                    price_tag = product_soup.find('span', class_="price__wrapper")
                    price = price_tag.text.strip() if price_tag else 'N/A'
                    
                    quantity_tag = product_soup.find('span', class_='price__unit')
                    quantity = quantity_tag.text.strip() if quantity_tag else 'N/A'
                    
                    product_name_tag = product_soup.find('span', class_='mod-article-tile__title')
                    product_name = product_name_tag.text.strip() if product_name_tag else 'N/A'
                    
                    # Update the DataFrame with the scraped data
                    df.at[index, 'product_name'] = product_name
                    df.at[index, 'product_price'] = price
                    df.at[index, 'product_quantity'] = quantity

                except Exception as e:
                    print(f"Error scraping {product_link}: {e}")

                # print(f"Product Name: {product_name}, Price: {price}, Quantity: {quantity}")
                # print("------------------------------------------------------")

            # Append the data for the current category to the main DataFrame
            df_aldi = pd.concat([df_aldi, df], ignore_index=True)

        except Exception as e:
            print(f"Error scraping category {category_name}: {e}")

    return df_aldi.drop_duplicates()
