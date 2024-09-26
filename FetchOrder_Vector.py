from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import pandas as pd
import numpy as np

def match(db_products, find_products):
    # Step 1: Fit the TF-IDF vectorizer on the database (only once)
    vectorizer = TfidfVectorizer()
    tfidf_db_matrix = vectorizer.fit_transform(db_products['product_name'])

    # Step 2: Transform the search list products into TF-IDF vectors
    tfidf_search_matrix = vectorizer.transform(find_products['Product'])

    # Step 3: Compute cosine similarity between the search products and database products
    # This will create a (len(find_products), len(db_products)) similarity matrix
    cosine_sim = cosine_similarity(tfidf_search_matrix, tfidf_db_matrix)

    # Step 4: For each product to find, get the top N most similar products
    top_n = 3  # Change this number to get more or fewer matches
    matched_products = []

    for i, search_product in enumerate(find_products['Product']):
        # Get the indices of the top N most similar products from the database
        top_n_indices = np.argsort(cosine_sim[i])[::-1][:top_n]
        top_n_similarities = cosine_sim[i][top_n_indices]
        
        # Create a list of matches for each product to find
        matches = pd.DataFrame({
            'product_to_find': search_product,
            'price': db_products.iloc[top_n_indices]['product_price'].values,
            'store_name': db_products.iloc[top_n_indices]['store_name'].values,
            'matched_product': db_products.iloc[top_n_indices]['product_name'].values,
            'similarity_score': top_n_similarities
        })
        
        matched_products.append(matches)

    return matched_products



def match_products(products):
    matched = []

    df_database=pd.read_csv('./scraping/df_all_products_std.csv')
    store_name=df_database['store_name'].unique()
    for store in store_name:
        df_store = df_database[df_database['store_name'] == store]
        matched_rows = match(df_store, products)
        matched.append(matched_rows)
    return matched