import pandas as pd
import sys

def load_excel_data(file_path):
    try:
        # Read the Excel file
        df = pd.read_excel(file_path)
        print("\n=== Excel File Loaded Successfully ===")
        print(f"Total Rows: {len(df)}")
        print("\n=== First 5 Rows ===")
        print(df.head().to_string())
        
        # Basic analysis
        if len(df) > 0:
            print("\n=== Basic Analysis ===")
            print("\nColumn Names:")
            for col in df.columns:
                print(f"- {col}")
            
            # Check for potential grouping columns
            potential_group_cols = ['age', 'ability', 'level', 'skill', 'group']
            found_cols = [col for col in df.columns if any(x in str(col).lower() for x in potential_group_cols)]
            
            if found_cols:
                print("\nPotential grouping columns found:")
                for col in found_cols:
                    print(f"- {col} (Unique values: {df[col].nunique()})")
        
        return df
        
    except Exception as e:
        print(f"\nError loading Excel file: {str(e)}")
        return None

if __name__ == "__main__":
    if len(sys.argv) > 1:
        file_path = sys.argv[1]
    else:
        file_path = "Ride Tribe Late Ski Adam test.xlsx"
    
    print(f"Analyzing file: {file_path}")
    data = load_excel_data(file_path)
