# University Library Book Lending System

## Project Overview

The University Library Book Lending System is a web-based platform designed to manage book lending operations for students and teachers within a university environment. The system allows users to browse, search, and borrow physical books, with digital alternatives available when physical copies are unavailable.

## Core Features

- **User Authentication**: Role-based access for students, teachers, and administrators
- **Book Catalog**: Comprehensive database of available books with search functionality
- **Borrowing System**: Management of book loans with configurable lending periods
- **Digital Content**: Access to digital copies when physical books are unavailable
- **Inventory Management**: Tracking of physical copies and their status
- **Reporting**: Statistical analysis of borrowing patterns and inventory status

## Technical Stack

- **Backend**: Django (Python web framework)
- **Frontend**: Tailwind CSS for styling
- **Database**: PostgreSQL
- **Version Control**: Git

## Project Structure

```
university-library/
├── accounts/             # User authentication and profiles
├── books/                # Book catalog and inventory management
├── borrowing/            # Loan processing and management
├── digital_content/      # Digital book handling
├── admin_dashboard/      # Administrative interface
├── reports/              # Reporting and analytics
├── static/               # Static files (CSS, JS)
├── templates/            # HTML templates
└── university_library/   # Main project settings
```

## Getting Started

### Prerequisites

- Python 3.8+
- PostgreSQL
- Node.js (for Tailwind CSS)

### Installation

1. **Clone the repository**
   ```
   git clone https://github.com/university/library-system.git
   cd library-system
   ```

2. **Set up virtual environment**
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install Python dependencies**
   ```
   pip install -r requirements.txt
   ```

4. **Configure environment variables**
   Create a `.env` file with the following:
   ```
   DEBUG=True
   SECRET_KEY=your-secret-key
   DATABASE_URL=postgresql://user:password@localhost:5432/library_db
   ```

5. **Run migrations**
   ```
   python manage.py migrate
   ```

6. **Install frontend dependencies**
   ```
   npm install
   ```

7. **Build CSS**
   ```
   npm run build-css
   ```

8. **Create superuser**
   ```
   python manage.py createsuperuser
   ```

9. **Run development server**
   ```
   python manage.py runserver
   ```

## Book Status System

Books in the system can have the following statuses:

- **Available**: Ready to be borrowed
- **Borrowed**: Currently checked out
- **Reserved**: Set aside for a specific user
- **Lost**: Reported missing
- **Deteriorated**: Damaged but still usable
- **To Remove**: Marked for removal from circulation
- **Removed**: No longer in the collection

## Borrowing Process

1. User searches for a book
2. System checks availability
3. If available, user selects loan period (3 days, 1 week, etc.)
4. System reserves the book and notifies user for pickup
5. If physical copy unavailable, system offers digital alternative
6. Books are automatically marked as overdue when loan period expires

## Scheduled Tasks

The system includes the following automated processes:

- Due date reminders (3 days, 1 day before due date)
- Automatic status changes for long-lost books (removed after 1 year)
- Processing of waitlisted reservations when books become available

## Development Guidelines

- Follow PEP 8 style guide for Python code
- Write unit tests for all core functionality
- Document API endpoints using docstrings
- Use feature branches for development
- Submit pull requests for code review

## Sprint Structure

The project is being developed in 2-week sprints with the following ceremonies:
- Sprint Planning (Day 1)
- Daily Standups (15 minutes each morning)
- Sprint Review (Last day)
- Sprint Retrospective (Last day)
- Backlog Refinement (Mid-sprint)

## Team

The project is being developed by a 5-person team with the following roles:
- Backend Specialist
- Authentication Specialist
- Frontend Specialist
- Full-stack (Catalog Focus)
- Full-stack (Reporting Focus)

## License

This project is proprietary and intended for use within the university only.