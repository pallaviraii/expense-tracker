# PennyPilot

PennyPilot is a Django web app to track income and expenses, with budgets, insights, and charts.

## Features
- User signup, login, logout (each user sees only their own data)
- Add, edit, delete income and expense transactions
- Custom categories
- Dashboard with total income, expense, and balance
- Pie chart (expenses by category) and bar chart (monthly expenses)
- Filter by type, category, and date range, plus search

## Tech Stack
Python, Django, SQLite, HTML, CSS, Bootstrap, JavaScript, Chart.js

## How to Run
1. Clone the repository
2. Create and activate a virtual environment
3. `pip install -r requirements.txt`
4. `python manage.py migrate`
5. `python manage.py createsuperuser`
6. `python manage.py runserver`
7. Open http://127.0.0.1:8000/

## Author
Pallavi
