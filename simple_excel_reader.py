import pandas as pd

def read_excel_simple(file_path):
    try:
        # Read the Excel file
        xls = pd.ExcelFile(file_path)
        print(f"File: {file_path}")
        print(f"Sheets: {xls.sheet_names}")
        
        # Read the first sheet
        df = pd.read_excel(file_path, sheet_name=0, header=None)
        
        # Find the first row with data
        first_data_row = 0
        for i in range(min(20, len(df))):  # Check first 20 rows
            if not df.iloc[i].isna().all():
                first_data_row = i
                break
                
        print(f"\nFirst data row: {first_data_row}")
        
        # Read the file again with the correct header
        df = pd.read_excel(file_path, sheet_name=0, header=first_data_row)
        
        # Print column names and first few rows
        print("\nColumns:")
        for i, col in enumerate(df.columns):
            print(f"{i+1}. {col}")
            
        print("\nFirst 5 rows of data:")
        print(df.head().to_string())
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    read_excel_simple("Ride Tribe Late Ski Adam test.xlsx")
