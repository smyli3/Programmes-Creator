# Authentication System

This module provides user authentication functionality for the Snowsports Program Manager application.

## Features

- User registration with email confirmation
- Secure password reset functionality
- Email address verification
- Password change functionality
- Account management (email change, password update)
- Secure session management
- Role-based access control (admin/user roles)

## Routes

### Authentication Routes
- `/login` - User login
- `/logout` - User logout
- `/register` - New user registration
- `/confirm/<token>` - Email confirmation
- `/confirm` - Resend confirmation email

### Password Management
- `/reset-password-request` - Request password reset
- `/reset-password/<token>` - Reset password with token
- `/change-password` - Change password (authenticated users only)

### Account Management
- `/change-email` - Request email change
- `/change-email/<token>` - Confirm email change with token

## Templates

### Authentication Templates
- `auth/base.html` - Base template for authentication pages
- `auth/login.html` - User login form
- `auth/register.html` - User registration form
- `auth/unconfirmed.html` - Email confirmation required page

### Email Templates
- `auth/email/base.html` - Base template for all emails
- `auth/email/confirm.html` - Email confirmation email
- `auth/email/reset_password.html` - Password reset email
- `auth/email/change_email.html` - Email change confirmation

## Forms

All forms use WTForms with CSRF protection and client-side validation.

### Available Forms
- `LoginForm` - User login
- `RegistrationForm` - New user registration
- `ChangePasswordForm` - Change password
- `PasswordResetRequestForm` - Request password reset
- `PasswordResetForm` - Reset password
- `ChangeEmailForm` - Change email address

## Security Features

- Password hashing using Werkzeug's security helpers
- CSRF protection on all forms
- Secure session management
- Password strength requirements
- Email verification for critical actions
- Rate limiting on authentication endpoints
- Secure password reset tokens with expiration

## Configuration

The following configuration variables are used by the authentication system:

```python
# Flask-Security settings
SECURITY_PASSWORD_SALT = 'your-password-salt'
SECURITY_CONFIRMABLE = True
SECURITY_RECOVERABLE = True
SECURITY_TRACKABLE = True
SECURITY_CHANGEABLE = True
SECURITY_SEND_REGISTER_EMAIL = True

# Email settings
MAIL_SERVER = 'smtp.example.com'
MAIL_PORT = 587
MAIL_USE_TLS = True
MAIL_USERNAME = 'noreply@example.com'
MAIL_PASSWORD = 'your-email-password'
MAIL_DEFAULT_SENDER = 'noreply@example.com'

# In development, you can suppress sending emails
MAIL_SUPPRESS_SEND = False  # Set to True in development
```

## Dependencies

- Flask-Login: User session management
- Flask-WTF: Form handling and CSRF protection
- Flask-Mail: Email sending
- Flask-Security-Too: Security features (optional)
- itsdangerous: Token generation and validation

## Usage

### Protecting Routes

Use the `@login_required` decorator to protect routes that require authentication:

```python
from flask_login import login_required

@app.route('/protected')
@login_required
def protected():
    return 'This is a protected route.'
```

### Checking User Authentication

In templates, you can check if a user is authenticated:

```html
{% if current_user.is_authenticated %}
    Welcome, {{ current_user.username }}!
{% else %}
    Please log in to continue.
{% endif %}
```

### Checking User Roles

To check if a user has a specific role:

```python
if current_user.has_role('admin'):
    # Admin-only functionality
    pass
```

## Testing

Test the authentication system by:
1. Registering a new account
2. Verifying the email address
3. Logging in with the new account
4. Testing password reset functionality
5. Testing email change functionality
6. Testing account deletion (if implemented)

## Security Considerations

- Always use HTTPS in production
- Set appropriate security headers
- Implement rate limiting on authentication endpoints
- Keep dependencies up to date
- Use strong password hashing (already implemented with Werkzeug)
- Log security-related events
- Implement account lockout after failed login attempts

## License

This module is part of the Snowsports Program Manager and is licensed under the MIT License.
