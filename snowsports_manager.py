import pandas as pd
from datetime import datetime
import os

class SnowsportsManager:
    def __init__(self, csv_file):
        self.csv_file = csv_file
        self.students = []
        self.groups = {}
        
    def load_data(self):
        """Load and clean the CSV data."""
        try:
            # Read CSV with proper encoding
            df = pd.read_csv(self.csv_file, encoding='utf-8-sig')
            
            # Clean up column names
            df.columns = [col.strip() for col in df.columns]
            
            # Convert date strings to datetime objects
            df['BirthDate'] = pd.to_datetime(df['BirthDate'], format='%d-%b-%y', errors='coerce')
            
            # Calculate age as of program start (assuming program starts in September 2025)
            program_start = datetime(2025, 9, 1)
            df['Age'] = (program_start - df['BirthDate']).dt.days // 365
            
            # Extract ability level from ProductDescription_1 if available
            df['AbilityLevel'] = df['ProductDescription_1'].str.extract(r'(?i)(beginner|intermediate|advanced)')
            
            # Store the cleaned data
            self.students = df.to_dict('records')
            return True
            
        except Exception as e:
            print(f"Error loading data: {e}")
            return False
    
    def create_groups(self, max_group_size=6):
        """Create groups based on age and ability."""
        if not self.students:
            print("No student data available. Please load data first.")
            return
            
        # Sort students by age and ability
        sorted_students = sorted(
            self.students, 
            key=lambda x: (x.get('Age', 0), x.get('AbilityLevel', ''))
        )
        
        # Create groups
        group_num = 1
        current_group = []
        
        for student in sorted_students:
            current_group.append(student)
            
            if len(current_group) >= max_group_size:
                self.groups[f"Group {group_num}"] = current_group
                group_num += 1
                current_group = []
        
        # Add the last group if it's not empty
        if current_group:
            self.groups[f"Group {group_num}"] = current_group
    
    def print_group_summary(self):
        """Print a summary of the created groups."""
        print("\n=== Snowsports Program Groups ===")
        print(f"Total Students: {len(self.students)}")
        print(f"Number of Groups: {len(self.groups)}")
        
        for group_name, members in self.groups.items():
            print(f"\n{group_name} ({len(members)} students):")
            print("-" * 40)
            for i, student in enumerate(members, 1):
                name = student.get('CustomerName', 'Unknown')
                age = student.get('Age', 'N/A')
                ability = student.get('AbilityLevel', 'Not specified').title()
                print(f"{i}. {name} (Age: {age}, Level: {ability})")
    
    def save_to_excel(self, output_file=None):
        """Save groups to an Excel file."""
        if not output_file:
            output_file = os.path.splitext(self.csv_file)[0] + "_groups.xlsx"
            
        with pd.ExcelWriter(output_file) as writer:
            for group_name, members in self.groups.items():
                df = pd.DataFrame(members)
                df.to_excel(writer, sheet_name=group_name, index=False)
                
        print(f"\nGroups saved to: {output_file}")

def main():
    # Initialize the manager
    csv_file = "Report CXV.csv"
    manager = SnowsportsManager(csv_file)
    
    # Load and process the data
    if manager.load_data():
        print("Data loaded successfully!")
        
        # Create groups
        manager.create_groups()
        
        # Print summary
        manager.print_group_summary()
        
        # Save to Excel
        manager.save_to_excel()
    else:
        print("Failed to load data. Please check the CSV file.")

if __name__ == "__main__":
    main()
