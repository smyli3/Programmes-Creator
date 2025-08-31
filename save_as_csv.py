import pandas as pd

try:
    # Read the Excel file
    df = pd.read_excel('Ride Tribe Late Ski Adam test.xlsx', header=None)
    
    # Save as CSV
    csv_file = 'program_data.csv'
    df.to_csv(csv_file, index=False, header=False)
    print(f"File saved as {csv_file}")
    
except Exception as e:
    print(f"Error: {e}")
