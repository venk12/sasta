import pandas as pd
import numpy as np
from thefuzz import process
from thefuzz import fuzz

df=pd.read_csv('sasta - revenue model - Sheet1.csv')

def match(df_database, product_name):
    store_name=df_database['store_name'].unique()

    results = []
    for store in store_name:
        df_store = df_database[df_database['store_name'] == store]
        matches =process.extract(product_name, df_store['product_name'], scorer=fuzz.token_sort_ratio, limit=3)
        
        # Create a DataFrame to display the results
        fuzzy_matches_df = pd.DataFrame({
            'Original': [product_name] * len(matches),
            'Matched': [match[0] for match in matches],
            'Score': [match[1] for match in matches],
            'Store': [store] * len(matches)
        })
        
        # Get top 3 matches for the current store
        top_matches = fuzzy_matches_df.nlargest(3, 'Score')
        results.append(top_matches)
    
    # Concatenate results from all stores
    final_results = pd.concat(results, ignore_index=True)
    return final_results


def match_products(products):
    matched = []
    df_database=pd.read_csv('./scraping/df_all_products_std.csv')
    for product in products:
        matched_rows = match(df_database, product)
        matched.append(matched_rows)
    return matched


# for product in df['Product']:
#     print("Matched products for:", product)
#     print(mm(product))
#     print('\n')

