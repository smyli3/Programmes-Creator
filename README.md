# Snowsports Program Manager

A web application for managing snowsports school programs, including student grouping, instructor assignment, and progress tracking.

## Features

- Upload student data from CSV or Excel files
- Automatically group students by age and ability level
- Export groups to Excel
- Responsive web interface
- Easy deployment to hosting platforms

## Prerequisites

- Python 3.7+
- pip (Python package manager)

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/snowsports-manager.git
   cd snowsports-manager
   ```

2. Create a virtual environment (recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install the required packages:
   ```bash
   pip install -r requirements.txt
   ```

## Running the Application

1. Start the Flask development server:
   ```bash
   python app.py
   ```

2. Open your web browser and go to:
   ```
   http://localhost:5000
   ```

## Usage

1. **Upload Data**: Click "Choose File" to upload a CSV or Excel file containing student information.
2. **Create Groups**: Set the maximum group size and click "Create Groups" to automatically group students by age and ability.
3. **Export**: Click "Export Groups" to download an Excel file with all groups and their members.

## File Format

The application expects the input file to have the following columns (case-sensitive):

- `CustomerName`: Student's full name
- `BirthDate`: Date of birth (format: DD-MMM-YY, e.g., 25-Dec-15)
- `ProductDescription_1`: Contains ability level (e.g., "Ride Tribe Late - Cardrona Ski - FT" where FT = First Timer)
- `ParentName`: Parent/guardian name
- `PrimaryEmergencyContact`: Emergency contact name
- `PrimaryEmergencyPhone`: Emergency contact phone number
- `FoodAllergy`: Any food allergies
- `Medication`: Any medications
- `SpecialCondition`: Any special conditions or notes

## Deployment

### Heroku

1. Install the [Heroku CLI](https://devcenter.heroku.com/articles/heroku-cli)
2. Login to Heroku:
   ```bash
   heroku login
   ```
3. Create a new Heroku app:
   ```bash
   heroku create your-app-name
   ```
4. Deploy your code:
   ```bash
   git push heroku main
   ```

### PythonAnywhere

1. Upload your code to PythonAnywhere
2. Create a new web app
3. Configure the WSGI file to point to `app:app`
4. Reload the web app

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Built with [Flask](https://flask.palletsprojects.com/)
- Styled with [Bootstrap 5](https://getbootstrap.com/)
- Icons by [Bootstrap Icons](https://icons.getbootstrap.com/)
