# Snowsports Program Manager

A comprehensive web application for managing snowsports programs, including student registration, group management, progress tracking, and instructor management with a complete authentication system.

## ✨ Features

### User Authentication & Authorization
- **User Registration** with email confirmation
- **Secure Login/Logout** with session management
- **Password Reset** via email
- **Role-based Access Control** (Admin/Instructor/User)
- **Account Management** (profile, password change, email update)

### Student Management
- Add, edit, and manage student information
- Track student progress and make notes
- View detailed student profiles with history
- Filter and search students by various criteria

### Group Organization
- Automatically create groups based on skill level and age
- Manual group assignment and adjustments
- Group progress tracking
- Instructor assignment to groups

### Data Management
- Import student data from Excel/CSV files
- Export reports in multiple formats (CSV, Excel, PDF)
- Data validation and error handling
- Backup and restore functionality

### User Interface
- **Responsive Design** works on all devices
- Intuitive dashboard with key metrics
- Real-time updates and notifications
- Accessible and user-friendly interface

## 🚀 Quick Start

### Prerequisites
- Python 3.8 or higher
- pip (Python package installer)
- Git (for version control)
- SQLite (included with Python)

### Installation

#### Windows
1. Clone the repository:
   ```powershell
   git clone https://github.com/yourusername/snowsports-program-manager.git
   cd snowsports-program-manager
   ```

2. Run the setup script:
   ```powershell
   .\setup.bat
   ```
   This will:
   - Create a virtual environment
   - Install all dependencies
   - Set up the database
   - Create an admin user

3. Start the application:
   ```powershell
   .\run_app.bat
   ```

#### macOS/Linux
1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/snowsports-program-manager.git
   cd snowsports-program-manager
   ```

2. Make the setup script executable and run it:
   ```bash
   chmod +x setup.sh
   ./setup.sh
   ```

3. Start the application:
   ```bash
   ./run_app.sh
   ```

4. Open your browser and navigate to `http://localhost:5000`

## ⚙️ Configuration

Create a `.env` file in the root directory (or copy from `.env.example`):

```env
# Application Settings
FLASK_APP=run.py
FLASK_ENV=development
SECRET_KEY=generate-a-secure-secret-key
SECURITY_PASSWORD_SALT=generate-a-secure-salt

# Database
DATABASE_URL=sqlite:///app.db

# Email Configuration
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-email-password
MAIL_DEFAULT_SENDER=your-email@gmail.com

# File Uploads
UPLOAD_FOLDER=uploads
MAX_CONTENT_LENGTH=16777216  # 16MB in bytes
```

## 📚 Documentation

### User Guide
1. **Registration & Login**
   - Register a new account with email confirmation
   - Log in with your credentials
   - Reset password if forgotten

2. **Dashboard**
   - View key metrics and recent activities
   - Quick access to important functions

3. **Students**
   - Add new students manually or import from file
   - View and edit student details
   - Track progress and add notes

4. **Groups**
   - Create and manage groups
   - Assign students to groups
   - Track group progress

5. **Reports**
   - Generate and export reports
   - View statistics and analytics

### File Format for Import

When uploading student data, use the following format:

| Column Name       | Required | Description                           |
|-------------------|----------|---------------------------------------|
| CustomerID        | Yes      | Unique student identifier             |
| CustomerName      | Yes      | Student's full name                   |
| BirthDate         | Yes      | Date of birth (YYYY-MM-DD)            |
| ProductDescription_1 | Yes   | Ability level (e.g., "Ski School IZ1") |
| ParentName        | Yes      | Parent/guardian name                  |
| Email             | Yes      | Contact email                         |
| Phone             | No       | Contact number                        |
| EmergencyPhone    | No       | Emergency contact number              |
| Address           | No       | Home address                          |
| City              | No       | City                                  |
| Country           | No       | Country                               |
| FoodAllergy       | No       | Any food allergies                    |
| DrugAllergy       | No       | Any drug allergies                    |
| Medication        | No       | Current medications                   |
| SpecialCondition  | No       | Any special conditions or notes       |

## 🛠 Development

### Project Structure
```
snowsports-program-manager/
├── app/                      # Application package
│   ├── static/               # Static files (CSS, JS, images)
│   ├── templates/            # HTML templates
│   ├── __init__.py           # Application factory
│   ├── models.py             # Database models
│   ├── routes/               # Application routes
│   ├── services/             # Business logic
│   └── utils/                # Utility functions
├── migrations/               # Database migrations
├── tests/                    # Test suite
├── .env.example              # Example environment variables
├── config.py                 # Configuration settings
├── init_db.py                # Database initialization
├── requirements.txt          # Dependencies
├── run.py                    # Application entry point
└── setup.bat                 # Setup script for Windows
```

### Running Tests
```bash
pytest
```

### Code Style
This project follows [PEP 8](https://www.python.org/dev/peps/pep-0008/) style guidelines.

## 🚀 Deployment

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
4. Set up the database:
   ```bash
   heroku addons:create heroku-postgresql:hobby-dev
   ```
5. Set environment variables:
   ```bash
   heroku config:set FLASK_APP=run.py
   heroku config:set SECRET_KEY=your-secret-key
   heroku config:set FLASK_ENV=production
   ```
6. Deploy the application:
   ```bash
   git push heroku main
   ```

### Docker
1. Build the Docker image:
   ```bash
   docker build -t snowsports-manager .
   ```
2. Run the container:
   ```bash
   docker run -d -p 5000:5000 --name snowsports-app snowsports-manager
   ```

## 📄 License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🤝 Contributing
Contributions are welcome! Please read our [contributing guidelines](CONTRIBUTING.md) to get started.

## 📧 Contact
For support or questions, please email support@example.com
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
