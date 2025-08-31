import pandas as pd

def get_excel_info(file_path):
    try:
        # Get all sheet names
        xls = pd.ExcelFile(file_path)
        print(f"\n=== Excel File: {file_path} ===")
        print(f"Sheets: {xls.sheet_names}")
        
        # Display first 5 rows of each sheet
        for sheet_name in xls.sheet_names:
            print(f"\n--- Sheet: {sheet_name} ---")
            try:
                df = pd.read_excel(file_path, sheet_name=sheet_name, nrows=10)
                print(f"Columns: {df.columns.tolist()}")
                print("\nFirst 5 rows:")
                print(df.head().to_string())
            except Exception as e:
                print(f"  Could not read sheet: {e}")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    excel_file = "Ride Tribe Late Ski Adam test.xlsx"
    get_excel_info(excel_file)
