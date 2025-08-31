import pandas as pd
import sys

def clean_column_names(columns):
    """Clean up column names by removing 'Unnamed' and extra spaces."""
    new_columns = []
    for col in columns:
        if pd.isna(col) or 'Unnamed:' in str(col):
            new_columns.append('')
        else:
            new_columns.append(str(col).strip())
    return new_columns

def load_excel_data(file_path):
    try:
        # Read the Excel file, skipping initial rows that don't contain data
        df = pd.read_excel(file_path, header=None)
        
        # Find the first row that contains actual column headers
        header_row = None
        for i, row in df.iterrows():
            if any('Product Date' in str(cell) for cell in row if pd.notna(cell)):
                header_row = i
                break
        
        if header_row is None:
            print("Could not find header row. Using first row as header.")
            header_row = 0
        
        # Read the file again with the correct header row
        df = pd.read_excel(file_path, header=header_row)
        
        # Clean up column names
        df.columns = clean_column_names(df.columns)
        
        # Remove completely empty rows and columns
        df = df.dropna(how='all')
        df = df.loc[:, ~df.columns.duplicated()]  # Remove duplicate columns
        
        print("\n=== Excel File Loaded Successfully ===")
        print(f"Total Rows: {len(df)}")
        print("\n=== First 5 Rows ===")
        print(df.head().to_string())
        
        # Basic analysis
        if len(df) > 0:
            print("\n=== Column Names ===")
            for i, col in enumerate(df.columns):
                print(f"{i+1}. '{col}'")
            
            # Check for potential data columns
            data_columns = [col for col in df.columns if col and len(col) > 0]
            if data_columns:
                print("\n=== Data Preview ===")
                for col in data_columns[:5]:  # Show first 5 data columns
                    if col in df.columns:
                        non_empty = df[col].count()
                        unique = df[col].nunique()
                        print(f"\nColumn: {col}")
                        print(f"Non-empty values: {non_empty}/{len(df)} ({(non_empty/len(df)*100):.1f}%)")
                        print(f"Unique values: {unique}")
                        if unique < 10:  # Show unique values if not too many
                            print(f"Values: {df[col].dropna().unique()}")
        
        return df
        
    except Exception as e:
        print(f"\nError loading Excel file: {str(e)}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    file_path = "Ride Tribe Late Ski Adam test.xlsx"
    print(f"Analyzing file: {file_path}")
    data = load_excel_data(file_path)
