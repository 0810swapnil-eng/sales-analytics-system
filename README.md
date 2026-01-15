**Sales Analytics System**

The Sales Analytics System is a modular Python framework designed for e-commerce businesses to process messy sales transaction data, fetch real-time product information from APIs, analyse customer and sales behaviour, and generate business-ready insights and reports.

This repository provides a clean, scalable project structure with separate modules for data ingestion, cleaning, validation, analytics, and external API integration.

**Features**
1. Robust Sales Data Loader (file_handler.py)
Reads sales data using multiple encodings (utf-8, latin-1, cp1252)
Handles missing files gracefully
Skips headers and empty lines
Cleans messy transaction rows including:
Fixing malformed numeric fields (removing commas)
Cleaning product names
Validating IDs (T, P, C)
Removing invalid records (zero or negative price/quantity)

2. Transaction Parser
Transforms raw file lines into structured dictionaries:
{
    "TransactionID": "T001",
    "Date": "2024-12-01",
    "ProductID": "P101",
    "ProductName": "Laptop",
    "Quantity": 2,
    "UnitPrice": 45000.0,
    "CustomerID": "C001",
    "Region": "North"
}


3. Transaction Validation & Filtering
Enforces business validation rules
Filters by:
Region
Minimum transaction amount
Maximum transaction amount
Produces summary metrics:
total input rows
invalid record count
region-based filters
amount-based filters
final usable dataset size

**Module Overview**

utils/file_handler.py

Contains:
read_sales_data(filename)
parse_transactions(raw_lines)
validate_and_filter(transactions, region=None, min_amount=None, max_amount=None)
Handles raw ingestion → cleaning → validation → filtering.

utils/data_processor.py

(Extendable)
Expected responsibilities:
Sales KPIs (revenue, units sold, average selling price)
Customer segmentation (RFM, frequency analysis)
Product performance analytics
Seasonality & trend detection

utils/api_handler.py

(Extendable)
Expected responsibilities:
Fetch real-time product metadata via external APIs
Handle API failures, retries, authentication
Cache results locally

main.py

Entry point of the system.
Responsible for:
Loading raw sales data
Parsing & validating transactions
Running analytics
Calling API enrichment
Saving outputs into /output
