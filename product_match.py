import pandas as pd
from rapidfuzz import process, fuzz

def fuzzy_match(item_name, choices, scorer=fuzz.WRatio, threshold=90):
    match = process.extractOne(item_name, choices, scorer=scorer)
    if match and match[1] >= threshold:
        return match[0]
    return None

def match_products(input_df):
    # Load the product database
    df_all_products = pd.read_csv("scraping/df_all_products.csv")
    
    # Ensure input DataFrame has the correct column names
    input_df.columns = ['Ingredients', 'Amount', 'Quantity']
    
    # Perform fuzzy matching
    matches = []
    for item in input_df['Ingredients']:
        match = fuzzy_match(item, df_all_products['product_name'], threshold=90)
        matches.append(match)
    
    # Add matches to the input DataFrame
    input_df['Matched Product'] = matches
    
    # Merge DataFrames
    merged_df = pd.merge(
        input_df, 
        df_all_products[['product_name', 'product_price', 'product_link', 'product_quantity', 'store_name']], 
        how='left', 
        left_on='Matched Product', 
        right_on='product_name'
    )
    
    # Drop the duplicate 'product_name' column
    merged_df.drop(columns=['product_name'], inplace=True)
    
    return merged_df