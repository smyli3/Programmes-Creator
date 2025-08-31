def read_csv_simple(file_path, num_lines=10):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            print(f"First {num_lines} lines of {file_path}:")
            print("-" * 80)
            for i, line in enumerate(f):
                if i >= num_lines:
                    break
                print(f"{i+1}: {line.strip()}")
    except Exception as e:
        print(f"Error reading file: {e}")

if __name__ == "__main__":
    read_csv_simple("Report CXV.csv")
