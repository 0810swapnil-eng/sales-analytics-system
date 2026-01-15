from datetime import datetime

def calculate_total_revenue(transactions):
    """
    Calculates total revenue from all transactions
    """
    return sum(float(tx['Quantity']) * float(tx['UnitPrice']) for tx in transactions)

def region_wise_sales(transactions):
    """
    Analyzes sales by region
    """
    if not transactions:
        return {}

    grand_total = calculate_total_revenue(transactions)
    stats = {}

    for tx in transactions:
        region = tx['Region']
        sale_amount = float(tx['Quantity']) * float(tx['UnitPrice'])
        
        if region not in stats:
            stats[region] = {
                'total_sales': 0.0,
                'transaction_count': 0
            }
        
        stats[region]['total_sales'] += sale_amount
        stats[region]['transaction_count'] += 1

    for region in stats:
        if grand_total > 0:
            stats[region]['percentage'] = round((stats[region]['total_sales'] / grand_total) * 100, 2)
        else:
            stats[region]['percentage'] = 0.0

    sorted_stats = sorted(
        stats.items(), 
        key=lambda item: item[1]['total_sales'], 
        reverse=True
    )

    return dict(sorted_stats)

def top_selling_products(transactions, n=5):
    """
    Finds top n products by total quantity sold
    """
    product_stats = {}

    for tx in transactions:
        name = tx['ProductName']
        qty = int(tx['Quantity'])
        revenue = float(tx['Quantity']) * float(tx['UnitPrice'])

        if name not in product_stats:
            product_stats[name] = {'total_qty': 0, 'total_revenue': 0.0}
        
        product_stats[name]['total_qty'] += qty
        product_stats[name]['total_revenue'] += revenue

    product_list = [
        (name, stats['total_qty'], stats['total_revenue']) 
        for name, stats in product_stats.items()
    ]

    product_list.sort(key=lambda x: x[1], reverse=True)

    return product_list[:n]

def customer_analysis(transactions):
    """
    Analyzes customer purchase patterns
    """
    stats = {}

    for tx in transactions:
        cust_id = tx['CustomerID']
        amount = float(tx['Quantity']) * float(tx['UnitPrice'])
        product = tx['ProductName']
        
        if cust_id not in stats:
            stats[cust_id] = {
                'total_spent': 0.0,
                'purchase_count': 0,
                'products_bought': set()
            }
        
        stats[cust_id]['total_spent'] += amount
        stats[cust_id]['purchase_count'] += 1
        stats[cust_id]['products_bought'].add(product)
    
    for cust_id in stats:
        count = stats[cust_id]['purchase_count']
        total = stats[cust_id]['total_spent']
        
        if count > 0:
            stats[cust_id]['avg_order_value'] = round(total / count, 2)
        else:
            stats[cust_id]['avg_order_value'] = 0.0
            
        stats[cust_id]['products_bought'] = list(stats[cust_id]['products_bought'])

    sorted_stats = sorted(
        stats.items(), 
        key=lambda item: item[1]['total_spent'], 
        reverse=True
    )

    return dict(sorted_stats)

def daily_sales_trend(transactions):
    """
    Analyzes sales trends by date
    """
    daily_stats = {}

    for tx in transactions:
        date_str = tx['Date']
        amount = float(tx['Quantity']) * float(tx['UnitPrice'])
        customer = tx['CustomerID']

        if date_str not in daily_stats:
            daily_stats[date_str] = {
                'revenue': 0.0,
                'transaction_count': 0,
                'unique_customers_set': set() 
            }
        
        daily_stats[date_str]['revenue'] += amount
        daily_stats[date_str]['transaction_count'] += 1
        daily_stats[date_str]['unique_customers_set'].add(customer)

    final_stats = {}
    for date, stats in daily_stats.items():
        final_stats[date] = {
            'revenue': stats['revenue'],
            'transaction_count': stats['transaction_count'],
            'unique_customers': len(stats['unique_customers_set'])
        }

    sorted_stats = sorted(
        final_stats.items(),
        key=lambda item: datetime.strptime(item[0], '%Y-%m-%d')
    )

    return dict(sorted_stats)

def find_peak_sales_day(transactions):
    """
    Identifies the date with highest revenue
    """
    if not transactions:
        return None

    daily_stats = {}

    for tx in transactions:
        date_str = tx['Date']
        amount = float(tx['Quantity']) * float(tx['UnitPrice'])

        if date_str not in daily_stats:
            daily_stats[date_str] = {'revenue': 0.0, 'count': 0}
        
        daily_stats[date_str]['revenue'] += amount
        daily_stats[date_str]['count'] += 1

    peak_day_item = max(daily_stats.items(), key=lambda item: item[1]['revenue'])
    
    date = peak_day_item[0]
    revenue = peak_day_item[1]['revenue']
    count = peak_day_item[1]['count']

    return (date, revenue, count)

def low_performing_products(transactions, threshold=10):
    """
    Identifies products with low sales

    Returns: list of tuples

    Expected Output Format:
    [
        ('Webcam', 4, 12000.0),  # (ProductName, TotalQuantity, TotalRevenue)
        ...
    ]
    """
    product_stats = {}

    # 1. Aggregate data by product
    for tx in transactions:
        name = tx['ProductName']
        qty = int(tx['Quantity'])
        revenue = float(tx['Quantity']) * float(tx['UnitPrice'])

        if name not in product_stats:
            product_stats[name] = {'total_qty': 0, 'total_revenue': 0.0}
        
        product_stats[name]['total_qty'] += qty
        product_stats[name]['total_revenue'] += revenue

    # 2. Filter by threshold and format as tuples
    low_performers = []
    for name, stats in product_stats.items():
        if stats['total_qty'] < threshold:
            low_performers.append((
                name, 
                stats['total_qty'], 
                stats['total_revenue']
            ))

    # 3. Sort by TotalQuantity ascending
    low_performers.sort(key=lambda x: x[1])

    return low_performers
