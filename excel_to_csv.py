import pandas as pd
import sys

def excel_to_csv(input_file, output_file=None):
    """Convert Excel file to CSV, handling various formats."""
    if output_file is None:
        output_file = input_file.replace('.xlsx', '.csv').replace('.xls', '.csv')
    
    try:
        # Try reading with different parameters
        try:
            df = pd.read_excel(input_file, engine='openpyxl')
        except:
            df = pd.read_excel(input_file, engine='xlrd')
        
        # Try to find the first row with actual data
        for i in range(min(10, len(df))):
            if not df.iloc[i].isna().all():
                df = pd.read_excel(input_file, skiprows=i)
                break
        
        # Save to CSV
        df.to_csv(output_file, index=False)
        print(f"Successfully converted to {output_file}")
        return True
        
    except Exception as e:
        print(f"Error: {e}")
        return False

if __name__ == "__main__":
    input_file = "Ride Tribe Late Ski Adam test.xlsx"
    excel_to_csv(input_file)
