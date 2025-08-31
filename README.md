# Snowsports Program Manager

A web application for managing snowsports programs, including student registration, group management, and progress tracking.

## Features

- **Student Management**: Add, edit, and manage student information
- **Group Organization**: Automatically create and manage student groups based on skill level and age
- **Progress Tracking**: Track student progress and make notes
- **Data Import/Export**: Import student data from Excel/CSV and export reports
- **Responsive Design**: Works on desktop and mobile devices

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/snowsports-program-manager.git
   cd snowsports-program-manager
   ```

2. Create a virtual environment and activate it:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install the required packages:
   ```bash
   pip install -r requirements.txt
   ```

4. Set up the database:
   ```bash
   flask db upgrade
   ```

5. Run the application:
   ```bash
   python run.py
   ```

6. Open your browser and navigate to `http://localhost:5000`

## Configuration

Create a `.env` file in the root directory with the following variables:

```
FLASK_APP=app.py
FLASK_ENV=development
SECRET_KEY=your-secret-key-here
DATABASE_URL=sqlite:///app.db
UPLOAD_FOLDER=uploads
```

## Usage

1. **Home Page**: Upload a CSV or Excel file containing student information
2. **Groups Page**: View and manage student groups, assign instructors, and track progress
3. **Student Profile**: View and edit individual student information and notes

## File Format

When uploading student data, use the following format:

| Column Name       | Description                           |
|-------------------|---------------------------------------|
| CustomerID        | Unique student identifier             |
| CustomerName      | Student's full name                   |
| BirthDate         | Date of birth (DD-MMM-YY)             |
| ProductDescription_1 | Ability level (e.g., "Ski School IZ1") |
| ParentName        | Parent/guardian name                  |
| Email             | Contact email                         |
| EmergencyPhone    | Emergency contact number              |
| FoodAllergy       | Any food allergies                    |
| DrugAllergy       | Any drug allergies                    |
| Medication        | Current medications                   |
| SpecialCondition  | Any special conditions or notes       |

## Development

To run the application in development mode:

```bash
python run.py
```

To run tests:

```bash
pytest
```

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
