import os

def read_sales_data(filename):
    """
    Reads sales data from file handling encoding issues 
    """
    encodings = ['utf-8', 'latin-1', 'cp1252']
    raw_lines = []

    if not os.path.exists(filename):
        print(f"Error: The file '{filename}' was not found.")
        return []

    for encoding in encodings:
        try:
            with open(filename, 'r', encoding=encoding) as file:
                # Skip the header row 
                next(file)
                for line in file:
                    clean_line = line.strip()
                    if clean_line:  # Remove empty lines 
                        raw_lines.append(clean_line)
            return raw_lines
        except (UnicodeDecodeError, StopIteration):
            continue
    
    return raw_lines

def parse_transactions(raw_lines):
    """
    Parses raw lines into clean list of dictionaries based on cleaning criteria 
    """
    parsed_data = []
    total_parsed = 0
    invalid_removed = 0
    
    for line in raw_lines:
        total_parsed += 1
        parts = line.split('|') [cite: 1]
        
        # Skip rows with incorrect number of fields 
        if len(parts) != 8:
            invalid_removed += 1
            continue
            
        try:
            # Clean commas from numbers 
            raw_qty = parts[4].replace(',', '')
            raw_price = parts[5].replace(',', '')
            
            qty = int(raw_qty) [cite: 1]
            price = float(raw_price) [cite: 1]
            
            # Cleaning Criteria:
            # - CustomerID/Region missing
            # - Quantity/UnitPrice <= 0
            # - TransactionID doesn't start with 'T'
            if (not parts[6].strip() or 
                not parts[7].strip() or 
                qty <= 0 or 
                price <= 0 or 
                not parts[0].startswith('T')):
                invalid_removed += 1
                continue
                
            # Remove commas from ProductName 
            clean_product_name = parts[3].replace(',', '')

            transaction = {
                'TransactionID': parts[0],
                'Date': parts[1],
                'ProductID': parts[2],
                'ProductName': clean_product_name,
                'Quantity': qty,
                'UnitPrice': price,
                'CustomerID': parts[6],
                'Region': parts[7]
            }
            parsed_data.append(transaction)
            
        except ValueError:
            invalid_removed += 1
            continue
    
    # Required output display
    print(f"Total records parsed: {total_parsed}")
    print(f"Invalid records removed: {invalid_removed}")
    print(f"Valid records after cleaning: {len(parsed_data)}")
            
    return parsed_data

def validate_and_filter(transactions, region=None, min_amount=None, max_amount=None):
    """
    Validates transactions and applies optional filters 
    """
    valid_transactions = []
    invalid_count = 0
    filtered_by_region = 0
    filtered_by_amount = 0
    
    # Validation Phase
    temp_valid = []
    for tx in transactions:
        is_valid = (
            tx['Quantity'] > 0 and 
            tx['UnitPrice'] > 0 and
            tx['TransactionID'].startswith('T') and
            tx['ProductID'].startswith('P') and
            tx['CustomerID'].startswith('C')
        )
        
        if is_valid:
            temp_valid.append(tx)
        else:
            invalid_count += 1

    # Information Display for user
    regions = sorted(list(set(t['Region'] for t in temp_valid)))
    amounts = [t['Quantity'] * t['UnitPrice'] for t in temp_valid]
    
    print(f"\n--- Filter Options ---")
    print(f"Available Regions: {', '.join(regions)}")
    if amounts:
        print(f"Transaction Amount Range: {min(amounts)} - {max(amounts)}")
    
    # Filtering Phase
    for tx in temp_valid:
        total_amt = tx['Quantity'] * tx['UnitPrice']
        
        if region and tx['Region'].lower() != region.lower():
            filtered_by_region += 1
            continue
            
        if (min_amount is not None and total_amt < min_amount) or \
           (max_amount is not None and total_amt > max_amount):
            filtered_by_amount += 1
            continue
            
        valid_transactions.append(tx)

    summary = {
        'total_input': len(transactions),
        'invalid': invalid_count,
        'filtered_by_region': filtered_by_region,
        'filtered_by_amount': filtered_by_amount,
        'final_count': len(valid_transactions)
    }
    
    return valid_transactions, invalid_count, summary
