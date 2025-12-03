# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**論文救火站 (APA Citation Generator)** is a Flask-based web application that helps academic writers with APA 7th edition citation formatting. It provides two main features:
1. **Free Citation Generator**: Uses CrossRef API to generate APA citations from DOI, title, keywords, or reference text (no login required)
2. **Document Checker** (Premium/Registered users): Analyzes Word documents (.doc/.docx) to detect citation format errors, missing references, and uncited references

The project includes a complete user authentication system with email verification, Google OAuth, and document management.

## Core Commands

### Development
```bash
# Install dependencies
pip install -r requirements.txt

# Run the Flask application (development mode)
python app.py

# Run all tests
python tests/run_all_tests.py

# Run a specific test
python tests/test_<name>.py
```

### Environment Setup
```bash
# Copy environment template
cp env.example .env

# Generate a secure SECRET_KEY
python -c "import secrets; print(secrets.token_hex(32))"
```

### Database
The application automatically creates database tables on first run. To reset:
```bash
# For SQLite (development)
rm apa_checker.db
python app.py

# The app uses SQLAlchemy and supports PostgreSQL for production
# Set DATABASE_URL in .env to switch databases
```

## Architecture

### Application Entry Point
- **app.py**: Main Flask application setup, routes registration, database initialization, and configuration loading

### Database Models (`models/`)
All models use SQLAlchemy ORM and are initialized in `models/__init__.py`:
- **User**: User accounts with email/password and Google OAuth support, email verification status, premium membership
- **Document**: User-uploaded documents with analysis results (JSON field)
- **EmailVerification**: Time-limited tokens for email verification
- **PasswordReset**: Time-limited tokens for password reset functionality
- **VisitorCount**: Global counter tracking total feature usage
- **InviteCode**: Admin-generated invitation codes for user registration

### Routes (`routes/`)
Blueprints pattern for modular routing:
- **citation.py**: Free citation generation API (`/api/generate_citation`, `/api/suggest_doi`)
- **auth.py**: Complete authentication system (register, login, logout, profile, email verification, password reset, Google OAuth)
- **admin.py**: Admin panel APIs for user management and invite code generation

### Services (`services/`)
Core business logic separated from routes:
- **crossref_service.py**: Integrates with CrossRef API to fetch academic paper metadata
- **apa_formatter.py**: Converts metadata to APA 7 format (both reference and citation formats)
- **document_analyzer.py**: Analyzes Word documents to extract citations and references, performs format checking
- **reference_parser.py**: Parses reference text to extract author names, years, and other citation components
- **email_service.py**: Handles email sending for verification and password reset

### Utilities (`utils/`)
- **decorators.py**: Custom decorators for route protection (`@login_required`, `@verified_required`)

### Document Analysis Flow
1. User uploads .doc/.docx file → `app.py:/api/analyze_document`
2. `DocumentAnalyzer` extracts text using python-docx library
3. Separates main text from References section (looks for "References" heading)
4. Parses references using `reference_parser.py` to build reference dictionary
5. Scans main text for citations using regex patterns (parenthetical and narrative styles)
6. Compares found citations against reference dictionary to detect:
   - Format errors (malformed citations)
   - Missing references (cited but not in References section)
   - Uncited references (in References but never cited)
7. Returns JSON with detailed analysis and suggestions

### Authentication Flow
- Standard email/password uses bcrypt for hashing
- Google OAuth implemented via Authlib
- Email verification tokens expire after 24 hours
- Password reset tokens are single-use and expire after 1 hour
- `DEV_MODE=True` in `.env` auto-verifies new users (development only)

### Permission Levels
- **Anonymous**: Can generate citations only
- **Registered (unverified)**: Same as anonymous, shown verification reminder
- **Verified**: Can upload documents for analysis, view document history
- **Premium**: Same as verified (future feature expansion planned)
- **Admin**: Can access `/admin` panel, manage users, generate invite codes (set via `ADMIN_EMAILS` in `.env`)

## Environment Variables

Critical variables in `.env`:
- **SECRET_KEY**: Flask session encryption (use `secrets.token_hex(32)`)
- **DATABASE_URL**: Database connection string (SQLite for dev, PostgreSQL for production)
- **DEV_MODE**: Set to `True` to skip email verification during development
- **MAIL_SERVER/MAIL_PORT/MAIL_USERNAME/MAIL_PASSWORD**: SMTP configuration (Gmail requires app-specific password)
- **GOOGLE_CLIENT_ID/GOOGLE_CLIENT_SECRET**: For Google OAuth login
- **ADMIN_EMAILS**: Comma-separated list of admin emails
- **PREMIUM_EMAILS**: Auto-upgrade these emails to premium on startup

## Database Configuration Notes

The app supports multiple database URL formats and automatically normalizes them:
- Converts `postgres://` to `postgresql+psycopg://` (for psycopg3 driver)
- Falls back to SQLite if no DATABASE_URL is set
- Check `app.py:28-42` for URL normalization logic

## Testing

Tests are in `tests/` directory and focus on:
- Citation detection patterns (parenthetical and narrative)
- Reference parsing (author extraction, year extraction)
- Edge cases (compound names, special characters, multiple citations)
- Format validation (semicolons, et al., ampersands)

Run all tests with `python tests/run_all_tests.py` which automatically discovers and runs all `test_*.py` files.

## Frontend Integration

Templates in `templates/` use vanilla JavaScript with Bootstrap 5:
- No frontend framework (React/Vue)
- AJAX calls to Flask JSON APIs
- Uses Flask-Login for session management
- Client-side form validation before API calls

## Branch Strategy

- **main**: Original version (free features only, no authentication)
- **feature/user-authentication**: Current branch with full auth system and document management

## Common Development Patterns

### Adding a New Route
1. Create or update blueprint in `routes/`
2. Use decorators from `utils/decorators.py` for auth
3. Import and register blueprint in `app.py`

### Adding a New Model
1. Create model class in `models/<name>.py`
2. Import in `models/__init__.py`
3. Database tables auto-create on next `app.py` run

### Modifying Citation Logic
1. Core APA formatting: `services/apa_formatter.py`
2. Citation detection: `services/document_analyzer.py` (regex patterns)
3. Reference parsing: `services/reference_parser.py`
4. Add tests in `tests/test_<feature>.py` to validate changes

## Security Considerations

- All passwords hashed with bcrypt (never stored in plaintext)
- CSRF protection via Flask-Login
- SQL injection prevented by SQLAlchemy ORM
- File uploads limited to .doc/.docx extensions
- Uploaded files deleted after analysis
- Token-based email verification and password reset
- User document isolation (users can only access their own documents)

## Deployment Notes

For production deployment:
1. Set `FLASK_DEBUG=False` and `DEV_MODE=False`
2. Use strong random `SECRET_KEY`
3. Switch from SQLite to PostgreSQL (set `DATABASE_URL`)
4. Configure HTTPS (required for OAuth)
5. Update `APP_URL` to production domain
6. Set Google OAuth redirect URIs in Google Console
7. Use production WSGI server (gunicorn included in requirements.txt)
