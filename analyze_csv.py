import pandas as pd

def analyze_csv(file_path):
    try:
        # Read the CSV file
        df = pd.read_csv(file_path)
        
        print(f"\n=== CSV File Analysis ===")
        print(f"File: {file_path}")
        print(f"Total Rows: {len(df)}")
        print(f"Total Columns: {len(df.columns)}")
        
        # Display column information
        print("\n=== Column Information ===")
        print("Index | Column Name | Non-Null Count | Data Type | Unique Values")
        print("-" * 80)
        for i, col in enumerate(df.columns):
            non_null = df[col].count()
            unique = df[col].nunique()
            dtype = df[col].dtype
            print(f"{i:5d} | {col[:40]:40} | {non_null:5d} | {str(dtype):8} | {unique}")
        
        # Show first few rows
        print("\n=== First 5 Rows ===")
        print(df.head().to_string())
        
        # Check for potential grouping columns
        potential_group_cols = ['age', 'ability', 'level', 'skill', 'group', 'name', 'participant']
        found_cols = [col for col in df.columns if any(x in str(col).lower() for x in potential_group_cols)]
        
        if found_cols:
            print("\n=== Potential Grouping Columns ===")
            for col in found_cols:
                print(f"\nColumn: {col}")
                print(f"Unique values: {df[col].nunique()}")
                if df[col].nunique() < 20:  # Show values if not too many
                    print(f"Values: {sorted(df[col].dropna().unique().tolist())}")
        
        return df
        
    except Exception as e:
        print(f"Error analyzing CSV: {str(e)}")
        return None

if __name__ == "__main__":
    csv_file = "Report CXV.csv"
    data = analyze_csv(csv_file)
