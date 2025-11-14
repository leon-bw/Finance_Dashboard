# Personal Finance Dashboard API 📊
A RESTful API for managing personal finances, tracking transactions, and monitoring budgets. Built with FastAPI and designed for easy integration with frontend applications.

## Why I Built This
Managing personal finance is a challenge that everyone faces. After trying various budgeting apps, I found them either too complex, lacking customisation and just not suited to my needs. More importantly, they treated money as purely numerical data ignoring the emotional and behavioral aspects that drive our spending decisions. Exploring this emotional connection is something I wanted to pursue

<br>

I wanted to build a solution that:

- **Goes Beyond Transaction Tracking:** Creates a holistic view of financial health that connects spending patterns to emotional well-being and behavioral insights

- **Improves Financial Literacy:** Educates users about their money habits, helping them understand not just what they spend, but why they spend

- **Recognises Emotional Spending:** Acknowledges that financial decisions are deeply personal and often influenced by our emotional state be it stress spending, retail therapy or impulse buying

- **Empowers Through Awareness:** Provides proactive budget alerts and spending insights that help users recognise patterns before they become problems, ultimately giving a sense of control and confidence

<br>
<br>

>Research shows that emotional spending accounts for a significant portion of budget overruns. By exploring the connection between feelings and finances, the aim is to:
>
>- Help users identify emotional spending triggers
>
>- Build healthier financial habits through self-awareness
>
>- Reduce financial stress by promoting mindful spending
>
>- Foster long-term financial confidence and control

<br>

## Features so far
- JWT Authentication - Secure user registration and login

<!-- - Demo Account - One-click demo access (no signup required) -->

- Transaction Management - Full CRUD operations for income and expense tracking

- Category System - Pre-defined and custom categories with color coding

- Budget Tracking - Set budgets with alerts and progress monitoring

<!-- - Financial Analytics - Dashboard with spending insights and trends -->

- Auto-Generated Documentation - Interactive API docs via Swagger UI

<br>
<br>

## API Documentation

#### Authentication Endpoints

| Method |  Endpoint |  Description |
| -------- | -------- | -------- |
POST |  /auth/register |    Create new user account
POST |  /auth/login |   Login with username/password
POST |  /auth/demo-login |  Quick demo access (no password)
GET |   /auth/me |  Get current user profile

#### Transaction Endpoints

| Method |  Endpoint |  Description |
| -------- | -------- | -------- |
GET |   /transactions/ |    List all transactions (with filters)
GET |   /transactions/{id} |    Get specific transaction
POST |  /transactions/ |    Create new transaction
PUT |   /transactions/{id} |    Update transaction
DELETE |    /transactions/{id} |    Delete transaction

#### Category Endpoints

| Method |  Endpoint |  Description |
| -------- | -------- | -------- |
GET |   /categories/ | List all categories
GET |   /categories/{id} |  Get specific category
POST |  /categories/ |  Create custom category
PUT |   /categories/{id} |  Update category
DELETE |    /categories/{id} |  Delete category

#### Budget Endpoints

| Method |  Endpoint |  Description
| -------- | -------- | -------- |
GET |   /budgets/ | List all budgets
GET |   /budgets/{id} | Get specific budget
POST |  /budgets/ | Create new budget
PUT |   /budgets/{id} | Update budget
DELETE |    /budgets/{id} | Delete budget

Example Request:

```
curl -X POST "http://127.0.0.1:8000/transactions/" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "amount": 50.00,
    "description": "Tesco Weekly Shop",
    "category": "Groceries",
    "type": "expense",
    "account": "Main Account",
    "currency": "GBP",
    "date": "2025-11-12T12:00:00Z"
  }'
  ```


### Query Parameters:

skip - Pagination offset (default: 0)

limit - Items per page (default: 50)

type - Filter by income/expense

category_id - Filter by category

start_date - Filter from date

end_date - Filter to date

<br>

## Project Structure
```
finance-dashboard/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI application 
│   ├── auth.py              # Authentication logic
│   ├── database.py          # Database configuration
│   ├── models.py            # SQLAlchemy models
│   ├── schemas.py           # Pydantic schemas
│   ├── seed_data.py         # Database seeding scripts
│   ├── routers/
│   │   ├── __init__.py
│   │   ├── auth.py          # Auth endpoints
│   │   ├── transactions.py  # Transaction endpoints
│   │   ├── categories.py    # Category endpoints
│   │   └── budgets.py       # Budget endpoints
│   └── tests/
│       ├── __init__.py
│       ├── conftest.py      # Pytest fixtures
│       ├── test_auth.py     # Authentication tests
│       └── test_transactions.py  # Transaction tests
├── .env                     # Environment variables
├── .gitignore
├── requirements.txt         # Python dependencies
└── README.md
```



