# Library Management System

## Project Overview

A web-based Library Management System built for university students and teachers to manage book lending operations. The system provides an efficient way to browse, borrow, and manage books with both physical and digital copies support.

## Core Features

- **User Management**
  - Role-based authentication (Students, Teachers, Administrators)
  - User profiles and borrowing history
  - Account management through `accounts` app

- **Book Management**
  - Comprehensive book catalog 
  - Multiple categories support
  - Physical and digital copy tracking
  - Real-time availability status

- **Borrowing System** (`appBibliotheque`)
  - Automated lending process
  - Configurable loan duration (default: 3 days)
  - Return date tracking
  - User and admin notes
  - Borrowing status updates

## Tech Stack

- **Backend:** Django (Python)
- **Frontend:** Tailwind CSS
- **Database:** SQLite3 (`db.sqlite3`)
- **Static Files:** FontAwesome 6.5.2

## Project Structure

```
lib-app-django/
├── accounts/                 # User authentication and profiles
├── appBibliotheque/         # Main library management functionality
├── bibliotheque/            # Project settings
├── static/                  # Static assets
├── media/                   # User uploaded content
└── theme/                   # UI theme components
```

## Installation

1. **Clone the repository**
```bash
git clone <repository-url>
cd lib-app-django
```

2. **Set up Python virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Apply database migrations**
```bash
python manage.py migrate
```

5. **Run development server**
```bash
python manage.py runserver
```

## Database Models

The system includes the following key models:
- User profiles
- Books catalog
- Categories
- Borrowing records (`Emprunter`) with:
  - Request date (`date_demande`)
  - Expected return date (`date_retour_prevue`)
  - Actual return date (`date_retour_reel`)
  - Duration in days (`duree_jours`)
  - Status tracking
  - User and admin notes

## Contributing

This project was developed using Agile methodology with 2-week sprint cycles. For contributions:

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

See the [LICENSE](LICENSE) file for details.