# Task Management System 🚀
A professional Django-based application to manage projects, tasks, and team collaborations.

##  Features Fixed
- **Security:** Hidden sensitive DB credentials using `.env`.
- **Database:** Optimized models, removed duplicate fields.
- **Features:** Added User Registration, Task Search, and Activity Logs.
- **Code Quality:** Fixed PEP8 indentation and sloppy syntax errors.

## Setup Instructions
1. **Clone & Environment:**
   `python -m venv venv`
   `source venv/bin/activate` (or `venv\Scripts\activate`)
2. **Install Dependencies:**
   `pip install -r requirements.txt`
3. **Environment Variables:**
   Create a `.env` file with `SECRET_KEY` and `DB_PASSWORD`.
4. **Database Setup:**
   `python manage.py makemigrations`
   `python manage.py migrate`
5. **Run Project:**
   `python manage.py runserver`