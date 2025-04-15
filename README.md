# Venue Booking & Reservation System

A dynamic and responsive web application for booking and managing venues, built with Django, TailwindCSS, HTMX, and Alpine.js. This application follows maintainable code organization principles with a modular design.

## 🚀 Features
- Browse, filter, and book venues
- Real-time availability and booking confirmation
- Venue manager dashboard for venue owners
- Admin management for venues, bookings, and availability
- Dynamic UI with HTMX and Alpine.js
- Maintainable code organization with modular design

## 🛠 Tech Stack
- **Backend:** Django (Python)
- **Frontend Styling:** TailwindCSS
- **Dynamic Interactions:** HTMX + Alpine.js
- **Templating:** Django Templates
- **Database:** SQLite (default, can use PostgreSQL/MySQL)

## 🏗️ Getting Started

### 1. Clone the Repository
```bash
git clone https://github.com/lanzy-lanzy/venue.git
cd venue
```

### 2. Create and Activate a Virtual Environment
```bash
python -m venv venv
# On Windows:
uv venv --python=3.13
uv pip install -r requirements.txt
# On macOS/Linux:
source venv/bin/activate
```

### 3. Install Dependencies
The project uses pyproject.toml for dependency management. You can install dependencies using pip:

```bash
# Create requirements.txt from pyproject.toml
pip install tomli
python -c "import tomli; open('requirements.txt', 'w').write('\n'.join([dep.split('==')[0] for dep in tomli.loads(open('pyproject.toml', 'rb').read())['project']['dependencies']]))"

# Install dependencies
pip install -r requirements.txt
```

Alternatively, if you have pip 23.0+ or a tool like uv installed:
```bash
pip install -e .
```

### 4. Apply Migrations
```bash
python manage.py migrate
```

### 5. Create a Superuser (Admin)
```bash
python manage.py createsuperuser
```

### 6. Run the Development Server
```bash
python manage.py runserver
```
Visit [http://127.0.0.1:8000/](http://127.0.0.1:8000/) in your browser.

## 🗂 Project Structure
- `venue/` — Main Django project settings
- `booking/` — Main Django app
  - `models/` — Database models (separated by entity)
  - `views/` — View functions (separated by functionality)
  - `forms.py` — Form definitions
  - `decorators.py` — Custom decorators
  - `middleware.py` — Custom middleware
  - `context_processors.py` — Custom context processors
  - `management/commands/` — Custom management commands
- `templates/` — Django HTML templates
  - `booking/` — Templates for booking views
  - `manager/` — Templates for venue manager views
  - `auth/` — Templates for authentication
  - `partials/` — Reusable template partials
- `static/` — Static files (CSS, JS, images)
- `media/` — User-uploaded files

## ⚙️ Customization
- Update venue categories, time slots, and booking logic in the respective model files under `booking/models/`.
- Modify view logic in the appropriate files under `booking/views/`.
- Adjust UI in the template files under `templates/`.

## 📚 Useful Commands
- `python manage.py runserver` — Start local server
- `python manage.py makemigrations` — Create migrations
- `python manage.py migrate` — Apply migrations
- `python manage.py createsuperuser` — Create admin user
- `python manage.py collectstatic` — Collect static files
- `python manage.py create_sample_data` — Create sample data for testing

## 📖 Learn More
- [Django Documentation](https://docs.djangoproject.com/)
- [TailwindCSS](https://tailwindcss.com/)
- [HTMX](https://htmx.org/)
- [Alpine.js](https://alpinejs.dev/)

## 🔧 Troubleshooting

### Common Issues

1. **Missing Templates**: Make sure the `templates` directory exists and contains the necessary HTML files.
   ```bash
   mkdir -p templates/booking templates/manager templates/auth templates/partials
   ```

2. **Static Files Not Loading**: Ensure your static files are properly configured in settings.py and collected.
   ```bash
   python manage.py collectstatic
   ```

3. **Database Errors**: If you encounter database issues, try resetting migrations.
   ```bash
   python manage.py makemigrations
   python manage.py migrate --run-syncdb
   ```

4. **Testing the Application**: To quickly test the application with sample data:
   ```bash
   python manage.py create_sample_data
   ```
   This will create sample users, venues, time slots, and bookings. You can log in with:
   - Regular user: username `user1`, password `password`
   - Venue manager: username `manager1`, password `password`
   - Admin: username `admin`, password `admin`

---

Feel free to customize this app for your needs!
