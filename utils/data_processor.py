import os
from datetime import datetime

# --- Existing Analysis Functions ---

def calculate_total_revenue(transactions):
    """Calculates total revenue from all transactions"""
    return sum(float(tx['Quantity']) * float(tx['UnitPrice']) for tx in transactions)

def region_wise_sales(transactions):
    """Analyzes sales by region"""
    if not transactions:
        return {}

    grand_total = calculate_total_revenue(transactions)
    stats = {}

    for tx in transactions:
        region = tx['Region']
        sale_amount = float(tx['Quantity']) * float(tx['UnitPrice'])
        
        if region not in stats:
            stats[region] = {'total_sales': 0.0, 'transaction_count': 0}
        
        stats[region]['total_sales'] += sale_amount
        stats[region]['transaction_count'] += 1

    for region in stats:
        if grand_total > 0:
            stats[region]['percentage'] = round((stats[region]['total_sales'] / grand_total) * 100, 2)
        else:
            stats[region]['percentage'] = 0.0

    sorted_stats = sorted(stats.items(), key=lambda item: item[1]['total_sales'], reverse=True)
    return dict(sorted_stats)

def top_selling_products(transactions, n=5):
    """Finds top n products by total quantity sold"""
    product_stats = {}
    for tx in transactions:
        name = tx['ProductName']
        qty = int(tx['Quantity'])
        revenue = float(tx['Quantity']) * float(tx['UnitPrice'])
        if name not in product_stats:
            product_stats[name] = {'total_qty': 0, 'total_revenue': 0.0}
        product_stats[name]['total_qty'] += qty
        product_stats[name]['total_revenue'] += revenue

    product_list = [(name, stats['total_qty'], stats['total_revenue']) for name, stats in product_stats.items()]
    product_list.sort(key=lambda x: x[1], reverse=True)
    return product_list[:n]

def customer_analysis(transactions):
    """Analyzes customer purchase patterns"""
    stats = {}
    for tx in transactions:
        cust_id = tx['CustomerID']
        amount = float(tx['Quantity']) * float(tx['UnitPrice'])
        product = tx['ProductName']
        if cust_id not in stats:
            stats[cust_id] = {'total_spent': 0.0, 'purchase_count': 0, 'products_bought': set()}
        stats[cust_id]['total_spent'] += amount
        stats[cust_id]['purchase_count'] += 1
        stats[cust_id]['products_bought'].add(product)
    
    for cust_id in stats:
        count = stats[cust_id]['purchase_count']
        total = stats[cust_id]['total_spent']
        stats[cust_id]['avg_order_value'] = round(total / count, 2) if count > 0 else 0.0
        stats[cust_id]['products_bought'] = list(stats[cust_id]['products_bought'])

    sorted_stats = sorted(stats.items(), key=lambda item: item[1]['total_spent'], reverse=True)
    return dict(sorted_stats)

def daily_sales_trend(transactions):
    """Analyzes sales trends by date"""
    daily_stats = {}
    for tx in transactions:
        date_str = tx['Date']
        amount = float(tx['Quantity']) * float(tx['UnitPrice'])
        customer = tx['CustomerID']
        if date_str not in daily_stats:
            daily_stats[date_str] = {'revenue': 0.0, 'transaction_count': 0, 'unique_customers_set': set()}
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
    sorted_stats = sorted(final_stats.items(), key=lambda item: datetime.strptime(item[0], '%Y-%m-%d'))
    return dict(sorted_stats)

def find_peak_sales_day(transactions):
    """Identifies the date with highest revenue"""
    if not transactions: return None
    daily_stats = {}
    for tx in transactions:
        date_str = tx['Date']
        amount = float(tx['Quantity']) * float(tx['UnitPrice'])
        if date_str not in daily_stats: daily_stats[date_str] = {'revenue': 0.0, 'count': 0}
        daily_stats[date_str]['revenue'] += amount
        daily_stats[date_str]['count'] += 1
    peak_day_item = max(daily_stats.items(), key=lambda item: item[1]['revenue'])
    return (peak_day_item[0], peak_day_item[1]['revenue'], peak_day_item[1]['count'])

def low_performing_products(transactions, threshold=10):
    """Identifies products with low sales"""
    product_stats = {}
    for tx in transactions:
        name = tx['ProductName']
        qty = int(tx['Quantity'])
        revenue = float(tx['Quantity']) * float(tx['UnitPrice'])
        if name not in product_stats: product_stats[name] = {'total_qty': 0, 'total_revenue': 0.0}
        product_stats[name]['total_qty'] += qty
        product_stats[name]['total_revenue'] += revenue
    low_performers = [(name, stats['total_qty'], stats['total_revenue']) for name, stats in product_stats.items() if stats['total_qty'] < threshold]
    low_performers.sort(key=lambda x: x[1])
    return low_performers

# --- NEW REPORT GENERATION FUNCTION ---

def generate_sales_report(transactions, enriched_transactions, output_file='output/sales_report.txt'):
    """
    Generates a comprehensive formatted text report
    """
    # Ensure output directory exists
    directory = os.path.dirname(output_file)
    if directory and not os.path.exists(directory):
        try:
            os.makedirs(directory)
        except OSError:
            pass

    # --- 1. PREPARE DATA ---
    total_revenue = calculate_total_revenue(transactions)
    total_tx = len(transactions)
    avg_order_val = total_revenue / total_tx if total_tx > 0 else 0
    
    dates = [t['Date'] for t in transactions]
    date_range = f"{min(dates)} to {max(dates)}" if dates else "N/A"
    
    region_stats = region_wise_sales(transactions)
    top_products = top_selling_products(transactions, n=5)
    top_customers = list(customer_analysis(transactions).items())[:5]
    daily_trend = daily_sales_trend(transactions)
    
    peak_day_info = find_peak_sales_day(transactions)
    low_performers = low_performing_products(transactions)
    
    # API Enrichment Stats
    unique_products = set(tx['ProductID'] for tx in enriched_transactions)
    successful_enrichments = set(tx['ProductID'] for tx in enriched_transactions if tx.get('API_Match'))
    failed_enrichments = unique_products - successful_enrichments
    success_rate = (len(successful_enrichments) / len(unique_products) * 100) if unique_products else 0

    # --- 2. BUILD REPORT STRING ---
    lines = []
    
    # HEADER
    lines.append("=" * 44)
    lines.append(f"{'SALES ANALYTICS REPORT':^44}")
    lines.append(f" Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S'):^32}")
    lines.append(f" Records Processed: {total_tx:<24}")
    lines.append("=" * 44)
    lines.append("")

    # OVERALL SUMMARY
    lines.append("OVERALL SUMMARY")
    lines.append("-" * 44)
    lines.append(f"Total Revenue:       ₹{total_revenue:,.2f}")
    lines.append(f"Total Transactions:  {total_tx}")
    lines.append(f"Average Order Value: ₹{avg_order_val:,.2f}")
    lines.append(f"Date Range:          {date_range}")
    lines.append("")

    # REGION-WISE PERFORMANCE
    lines.append("REGION-WISE PERFORMANCE")
    lines.append("-" * 44)
    lines.append(f"{'Region':<12} {'Sales':<15} {'% of Total':<12} {'Transactions'}")
    for region, stats in region_stats.items():
        lines.append(f"{region:<12} ₹{stats['total_sales']:<14,.0f} {stats['percentage']:>6.2f}% {stats['transaction_count']:>12}")
    lines.append("")

    # TOP 5 PRODUCTS
    lines.append("TOP 5 PRODUCTS")
    lines.append("-" * 60)
    lines.append(f"{'Rank':<6} {'Product Name':<25} {'Qty Sold':<10} {'Revenue'}")
    for i, (name, qty, rev) in enumerate(top_products, 1):
        lines.append(f"{i:<6} {name[:24]:<25} {qty:<10} ₹{rev:,.0f}")
    lines.append("")

    # TOP 5 CUSTOMERS
    lines.append("TOP 5 CUSTOMERS")
    lines.append("-" * 60)
    lines.append(f"{'Rank':<6} {'Customer ID':<15} {'Total Spent':<15} {'Orders'}")
    for i, (cid, stats) in enumerate(top_customers, 1):
        lines.append(f"{i:<6} {cid:<15} ₹{stats['total_spent']:<14,.0f} {stats['purchase_count']}")
    lines.append("")

    # DAILY SALES TREND
    lines.append("DAILY SALES TREND")
    lines.append("-" * 60)
    lines.append(f"{'Date':<12} {'Revenue':<15} {'Tx Count':<10} {'Unique Cust'}")
    for date, stats in daily_trend.items():
        lines.append(f"{date:<12} ₹{stats['revenue']:<14,.0f} {stats['transaction_count']:<10} {stats['unique_customers']}")
    lines.append("")

    # PRODUCT PERFORMANCE ANALYSIS
    lines.append("PRODUCT PERFORMANCE ANALYSIS")
    lines.append("-" * 44)
    if peak_day_info:
        lines.append(f"Best Selling Day: {peak_day_info[0]} (Rev: ₹{peak_day_info[1]:,.0f})")
    else:
        lines.append("Best Selling Day: N/A")
    
    if low_performers:
        lines.append(f"Low Performing Products (<10 qty): {len(low_performers)} found")
        # List first 3 as sample
        names = [p[0] for p in low_performers[:3]]
        lines.append(f"Sample: {', '.join(names)}...")
    else:
        lines.append("Low Performing Products: None")
        
    lines.append("\nAvg Transaction Value per Region:")
    for region, stats in region_stats.items():
        avg_reg = stats['total_sales'] / stats['transaction_count'] if stats['transaction_count'] else 0
        lines.append(f"  - {region:<10}: ₹{avg_reg:,.2f}")
    lines.append("")

    # API ENRICHMENT SUMMARY
    lines.append("API ENRICHMENT SUMMARY")
    lines.append("-" * 44)
    lines.append(f"Total Unique Products: {len(unique_products)}")
    lines.append(f"Successfully Enriched: {len(successful_enrichments)}")
    lines.append(f"Success Rate:          {success_rate:.2f}%")
    
    if failed_enrichments:
        lines.append("\nProducts Not Found in API:")
        for pid in list(failed_enrichments)[:5]: # Show max 5 failures
            lines.append(f"  - {pid}")
        if len(failed_enrichments) > 5:
            lines.append(f"  ... and {len(failed_enrichments)-5} more")
    else:
        lines.append("\nAll products successfully enriched!")

    # --- 3. WRITE TO FILE ---
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write('\n'.join(lines))
        print(f"Report successfully generated at: {output_file}")
    except IOError as e:
        print(f"Error writing report: {e}")
        
