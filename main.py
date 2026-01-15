import sys
import os

# Ensure the script can locate the utils package
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.file_handler import read_sales_data, parse_transactions, validate_and_filter
from utils.data_processor import (
    calculate_total_revenue, 
    region_wise_sales, 
    top_selling_products, 
    generate_sales_report
)
from utils.api_handler import (
    fetch_all_products, 
    create_product_mapping, 
    enrich_sales_data, 
    save_enriched_data
)

def main():
    """
    Main execution function orchestrating the Sales Analytics System.
    """
    print("=" * 40)
    print("SALES ANALYTICS SYSTEM")
    print("=" * 40 + "\n")

    try:
        # --- Step 1 & 2: Read Data ---
        print("[1/10] Reading sales data...")
        # Assuming data folder is in the same directory as main.py
        raw_lines = read_sales_data('data/sales_data.txt')
        if not raw_lines:
            print("Error: No data found or file is empty.")
            return
        print(f"✓ Successfully read {len(raw_lines)} lines\n")

        # --- Step 3: Parse and Clean ---
        print("[2/10] Parsing and cleaning data...")
        # Note: parse_transactions prints its own summary (Total/Invalid/Valid)
        cleaned_transactions = parse_transactions(raw_lines)
        print(f"✓ Parsed {len(cleaned_transactions)} valid records\n")

        # --- Step 4 & 5: Filter Options ---
        print("[3/10] Filter Options Available:")
        
        # Display available options without applying filter yet (dry run)
        _, _, temp_summary = validate_and_filter(cleaned_transactions)
        
        user_input = input("\nDo you want to filter data? (y/n): ").strip().lower()
        
        final_transactions = cleaned_transactions
        
        if user_input == 'y':
            print("\n--- Filter Criteria ---")
            region_input = input("Enter Region (Leave empty to skip): ").strip()
            min_amt_input = input("Enter Min Amount (Leave empty to skip): ").strip()
            max_amt_input = input("Enter Max Amount (Leave empty to skip): ").strip()

            # Convert inputs safely
            region_filter = region_input if region_input else None
            min_filter = float(min_amt_input) if min_amt_input else None
            max_filter = float(max_amt_input) if max_amt_input else None

            # Apply Filter
            filtered_data, _, _ = validate_and_filter(
                cleaned_transactions, 
                region=region_filter, 
                min_amount=min_filter, 
                max_amount=max_filter
            )
            final_transactions = filtered_data
            print(f"✓ Filter applied. {len(final_transactions)} records remain.")
        else:
            print("✓ Proceeding with full dataset.")
        print()

        # --- Step 6 & 7: Validate ---
        print("[4/10] Validating transactions...")
        # Re-validating final set to confirm numbers for next steps
        valid_final, invalid_final, summary_final = validate_and_filter(final_transactions)
        print(f"✓ Valid: {summary_final['final_count']} | Invalid/Filtered Out: {summary_final['invalid'] + summary_final['filtered_by_region'] + summary_final['filtered_by_amount']}\n")

        if not valid_final:
            print("Error: No valid transactions available to process.")
            return

        # --- Step 8: Perform Analysis ---
        print("[5/10] Analyzing sales data...")
        # We perform a quick check of key metrics here
        _ = calculate_total_revenue(valid_final)
        _ = region_wise_sales(valid_final)
        _ = top_selling_products(valid_final)
        print("✓ Analysis complete\n")

        # --- Step 9: Fetch API Data ---
        print("[6/10] Fetching product data from API...")
        api_products = fetch_all_products()
        if not api_products:
            print("Warning: API fetch failed. Enrichment will be skipped (API fields will be empty).")
        else:
            print(f"✓ Fetched {len(api_products)} products\n")

        # --- Step 10: Enrich Data ---
        print("[7/10] Enriching sales data...")
        product_map = create_product_mapping(api_products)
        enriched_data = enrich_sales_data(valid_final, product_map)
        
        # Calculate success rate for display
        matched = sum(1 for tx in enriched_data if tx.get('API_Match'))
        total = len(enriched_data)
        percentage = (matched / total * 100) if total else 0
        print(f"✓ Enriched {matched}/{total} transactions ({percentage:.1f}%)\n")

        # --- Step 11: Save Enriched Data ---
        print("[8/10] Saving enriched data...")
        save_enriched_data(enriched_data, 'data/enriched_sales_data.txt')
        print("✓ Saved to: data/enriched_sales_data.txt\n")

        # --- Step 12: Generate Report ---
        print("[9/10] Generating report...")
        generate_sales_report(valid_final, enriched_data, 'output/sales_report.txt')
        print("✓ Report saved to: output/sales_report.txt\n")

        # --- Step 13: Completion ---
        print("[10/10] Process Complete!")
        print("========================================")

    except Exception as e:
        print("\n!!! CRITICAL ERROR !!!")
        print(f"An unexpected error occurred: {e}")
        print("The program will now exit safely.")
        print("========================================")

if __name__ == "__main__":
    main()
