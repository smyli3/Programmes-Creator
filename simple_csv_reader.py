import csv

def read_csv_file(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8-sig') as file:
            reader = csv.reader(file)
            headers = next(reader)  # Get header row
            print("\n=== CSV Headers ===")
            for i, header in enumerate(headers, 1):
                print(f"{i}. {header}")
            
            print("\n=== First 5 Rows ===")
            for i, row in enumerate(reader):
                if i >= 5:  # Only show first 5 rows
                    break
                print(f"\nRow {i+1}:")
                for header, value in zip(headers, row):
                    print(f"  {header}: {value}")
                    
    except Exception as e:
        print(f"Error reading file: {e}")

if __name__ == "__main__":
    read_csv_file("Report CXV.csv")
