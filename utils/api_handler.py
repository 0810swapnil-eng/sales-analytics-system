import requests
import os

def fetch_all_products():
    """
    Fetches all products from DummyJSON API
    """
    url = "https://dummyjson.com/products"
    params = {'limit': 100}

    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        return data.get('products', [])

    except requests.exceptions.RequestException as e:
        print(f"API Request Failed: {e}")
        return []

def create_product_mapping(api_products):
    """
    Creates a mapping of product IDs to product info
    """
    mapping = {}
    if not api_products:
        return mapping

    for product in api_products:
        p_id = product.get('id')
        if p_id is not None:
            mapping[p_id] = {
                'title': product.get('title'),
                'category': product.get('category'),
                'brand': product.get('brand'),
                'rating': product.get('rating')
            }
    return mapping

def enrich_sales_data(transactions, product_mapping):
    """
    Enriches transaction data with API product information
    
    Returns: list of enriched transaction dictionaries
    """
    enriched_transactions = []
    
    for tx in transactions:
        # Create a copy to avoid modifying original list in place
        enriched_tx = tx.copy()
        
        # Extract numeric ID (e.g., 'P101' -> 101)
        product_id_str = tx.get('ProductID', '')
        api_id = None
        
        try:
            if product_id_str.upper().startswith('P'):
                api_id = int(product_id_str[1:])
            else:
                api_id = int(product_id_str)
        except (ValueError, TypeError):
            api_id = None

        # Look up in mapping
        if api_id in product_mapping:
            info = product_mapping[api_id]
            enriched_tx['API_Category'] = info['category']
            enriched_tx['API_Brand'] = info['brand']
            enriched_tx['API_Rating'] = info['rating']
            enriched_tx['API_Match'] = True
        else:
            enriched_tx['API_Category'] = None
            enriched_tx['API_Brand'] = None
            enriched_tx['API_Rating'] = None
            enriched_tx['API_Match'] = False
            
        enriched_transactions.append(enriched_tx)

    return enriched_transactions

def save_enriched_data(enriched_transactions, filename='data/enriched_sales_data.txt'):
    """
    Saves enriched transactions back to file with pipe delimiter.
    
    Expected File Format:
    TransactionID|Date|...|API_Match
    """
    # Ensure directory exists
    directory = os.path.dirname(filename)
    if directory and not os.path.exists(directory):
        try:
            os.makedirs(directory)
        except OSError:
            pass 

    try:
        with open(filename, 'w', encoding='utf-8') as f:
            # Define Header
            header = [
                'TransactionID', 'Date', 'ProductID', 'ProductName', 
                'Quantity', 'UnitPrice', 'CustomerID', 'Region',
                'API_Category', 'API_Brand', 'API_Rating', 'API_Match'
            ]
            f.write('|'.join(header) + '\n')

            # Write Rows
            for tx in enriched_transactions:
                row = [
                    str(tx.get('TransactionID', '')),
                    str(tx.get('Date', '')),
                    str(tx.get('ProductID', '')),
                    str(tx.get('ProductName', '')),
                    str(tx.get('Quantity', '')),
                    str(tx.get('UnitPrice', '')),
                    str(tx.get('CustomerID', '')),
                    str(tx.get('Region', '')),
                    # Handle None values by converting to empty string or keeping valid data
                    str(tx.get('API_Category') if tx.get('API_Category') is not None else ''),
                    str(tx.get('API_Brand') if tx.get('API_Brand') is not None else ''),
                    str(tx.get('API_Rating') if tx.get('API_Rating') is not None else ''),
                    str(tx.get('API_Match', False))
                ]
                f.write('|'.join(row) + '\n')
                
        print(f"Successfully saved {len(enriched_transactions)} records to '{filename}'")
        
    except IOError as e:
        print(f"Error writing to file: {e}")
