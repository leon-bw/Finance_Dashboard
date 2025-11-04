from app.auth import get_password_hash

from .database import Session
from .models import Category, Transaction, User


def seed_default_categories():
    db = Session()

    try:
        default_categories = [
            # Income Categories
            {
                "name": "Salary",
                "type": "income",
                "description": "From a job or business",
                "icon": "💰",
                "colour": "#85BB65",  # green
            },
            {
                "name": "Freelance",
                "type": "income",
                "description": "From freelance work or side hustles",
                "icon": "💼",
                "colour": "#35B535",  # lime green
            },
            {
                "name": "Investments",
                "type": "income",
                "description": "Money received from investments",
                "icon": "📈",
                "colour": "#FFD700",  # gold
            },
            {
                "name": "Gifts",
                "type": "income",
                "description": "Received as gifts from friends and family",
                "icon": "🎁",
                "colour": "#D1F6FF",  # light blue
            },
            {
                "name": "Other",
                "type": "income",
                "description": "Other income",
                "icon": "🤑",
                "colour": "#999999",  # light gray
            },
            # Expense Categories
            {
                "name": "Food",
                "type": "expense",
                "description": "Restaurant meals and takeaways",
                "icon": "🍔",
                "colour": "#DB8400",  # orange
            },
            {
                "name": "Transport",
                "type": "expense",
                "description": "Public transport, fuel, parking and vehicle maintenance,",
                "icon": "🚗",
                "colour": "#2196F3",  # blue
            },
            {
                "name": "Housing",
                "type": "expense",
                "description": "Rent, mortgage, house maintenance",
                "icon": "🏠",
                "colour": "#8C92AC",  # gray
            },
            {
                "name": "Entertainment",
                "type": "expense",
                "description": "Entertainment such as movies, games, and subscriptions",
                "icon": "🎬",
                "colour": "#8B5CF6",  # purple - violet
            },
            {
                "name": "Health",
                "type": "expense",
                "description": "Medical expenses and fitness",
                "icon": "🏥",
                "colour": "#ED1B24",  # red
            },
            {
                "name": "Utilities",
                "type": "expense",
                "description": "Utilities such as electricity, water, gas and internet",
                "icon": "💡",
                "colour": "#FFFF33",  # yellow - electric
            },
            {
                "name": "Shopping",
                "type": "expense",
                "description": "Shopping for clothes, electronics, and other items",
                "icon": "🛍️",
                "colour": "#F6A5C1",  # light pink
            },
            {
                "name": "Groceries",
                "type": "expense",
                "description": "Groceries and household items",
                "icon": "🛒",
                "colour": "#457D00",  # green - vegetable
            },
            {
                "name": "Education",
                "type": "expense",
                "description": "Education and training",
                "icon": "📚",
                "colour": "#EDE6CA",  # eggshell
            },
            {
                "name": "Other",
                "type": "expense",
                "description": "Other expenses",
                "icon": "💸",
                "colour": "#333333",  # dark gray
            },
        ]

        categories_added = 0
        for cat_data in default_categories:
            existing_category = (
                db.query(Category)
                .filter(
                    Category.name == cat_data["name"], Category.type == cat_data["type"]
                )
                .first()
            )
            if not existing_category:
                new_category = Category(**cat_data, is_default=True)
                db.add(new_category)
                categories_added += 1

        db.commit()
        db.close()
        print(
            f"Default categories seeded successfully: {categories_added} new categories added"
        )

    except Exception as error:
        db.rollback()
        print(f"Error seeding categories: {error}")

    finally:
        db.close()


def seed_demo_user():
    db = Session()
    # Check id demo user exists
    try:
        demo_user = db.query(User).filter(User.is_demo).first()

        if not demo_user:
            demo_user = User(
                username="demo",
                email="demo@myfinanacecoach.com",
                first_name="Demo",
                last_name="User",
                hashed_password=get_password_hash("demo1234"),
                is_demo=True,
                is_active=True,
                monthly_budget=3500,
                currency_preference="GBP",
            )
            db.add(demo_user)
            db.commit()
            print("Demo user created: username = 'demo', password = 'demo1234'")
        else:
            print("Demo user already exists")
    except Exception as error:
        db.rollback()
        print(f"Error seeding demo user {error}")

    finally:
        db.close()


def seed_demo_transaction():
    db = Session()

    try:
        demo_user = db.query(User).filter(User.is_demo).first()
        if not demo_user:
            print("Demo user not found, run seed_demo_user first")

        demo_transactions = (
            db.query(Transaction).filter(Transaction.user_id == demo_user.id).count()
        )
        if demo_transactions > 0:
            print(
                f"Demo transactions already exist {demo_transactions} transactions in database"
            )

        transaction_template = {
            "Salary": [
                {
                    "description": "Monthly Salary",
                    "amount": 3500.00,
                    "type": "income",
                    "category": "Salary",
                    "frequency": "monthly",
                    "day": 25,
                }
            ],
            "Groceries": [
                {
                    "description": "Tesco Weekly Shop",
                    "amount_range": (45, 85),
                    "type": "expense",
                    "category": "Groceries",
                },
                {
                    "description": "Sainsbury's Groceries",
                    "amount_range": (30, 70),
                    "type": "expense",
                    "category": "Groceries",
                },
                {
                    "description": "Aldi Shopping",
                    "amount_range": (25, 55),
                    "type": "expense",
                    "category": "Groceries",
                },
                {
                    "description": "Lidl Weekly Shop",
                    "amount_range": (35, 65),
                    "type": "expense",
                    "category": "Groceries",
                },
            ],
            "Food": [
                {
                    "description": "Nando's Dinner",
                    "amount_range": (18, 35),
                    "type": "expense",
                    "category": "Food",
                },
                {
                    "description": "Domino's Pizza",
                    "amount_range": (15, 28),
                    "type": "expense",
                    "category": "Food",
                },
                {
                    "description": "Starbucks Coffee",
                    "amount_range": (3.5, 7.5),
                    "type": "expense",
                    "category": "Food",
                },
                {
                    "description": "McDonald's",
                    "amount_range": (6, 12),
                    "type": "expense",
                    "category": "Food",
                },
                {
                    "description": "Wagamama Lunch",
                    "amount_range": (12, 22),
                    "type": "expense",
                    "category": "Food",
                },
                {
                    "description": "Costa Coffee",
                    "amount_range": (3, 6),
                    "type": "expense",
                    "category": "Food",
                },
                {
                    "description": "Pizza Express",
                    "amount_range": (20, 40),
                    "type": "expense",
                    "category": "Food",
                },
            ],
            "Transport": [
                {
                    "description": "Shell Petrol",
                    "amount_range": (45, 75),
                    "type": "expense",
                    "category": "Transport",
                },
                {
                    "description": "TfL Oyster Top-up",
                    "amount_range": (20, 40),
                    "type": "expense",
                    "category": "Transport",
                },
                {
                    "description": "Uber Ride",
                    "amount_range": (8, 25),
                    "type": "expense",
                    "category": "Transport",
                },
                {
                    "description": "Car Park Fee",
                    "amount_range": (3, 12),
                    "type": "expense",
                    "category": "Transport",
                },
            ],
            "Entertainment": [
                {
                    "description": "Netflix Subscription",
                    "amount": 10.99,
                    "type": "expense",
                    "category": "Entertainment",
                    "frequency": "monthly",
                    "day": 5,
                },
                {
                    "description": "Spotify Premium",
                    "amount": 9.99,
                    "type": "expense",
                    "category": "Entertainment",
                    "frequency": "monthly",
                    "day": 12,
                },
                {
                    "description": "Amazon Prime",
                    "amount": 8.99,
                    "type": "expense",
                    "category": "Entertainment",
                    "frequency": "monthly",
                    "day": 18,
                },
                {
                    "description": "Cinema Tickets",
                    "amount_range": (15, 30),
                    "type": "expense",
                    "category": "Entertainment",
                },
                {
                    "description": "PlayStation Store",
                    "amount_range": (10, 50),
                    "type": "expense",
                    "category": "Entertainment",
                },
            ],
            "Shopping": [
                {
                    "description": "Amazon Purchase",
                    "amount_range": (15, 150),
                    "type": "expense",
                    "category": "Shopping",
                },
                {
                    "description": "ASOS Order",
                    "amount_range": (30, 80),
                    "type": "expense",
                    "category": "Shopping",
                },
                {
                    "description": "Zara Shopping",
                    "amount_range": (35, 90),
                    "type": "expense",
                    "category": "Shopping",
                },
                {
                    "description": "H&M Purchase",
                    "amount_range": (20, 60),
                    "type": "expense",
                    "category": "Shopping",
                },
            ],
            "Health": [
                {
                    "description": "PureGym Membership",
                    "amount": 29.99,
                    "type": "expense",
                    "category": "Health",
                    "frequency": "monthly",
                    "day": 1,
                },
                {
                    "description": "Boots Pharmacy",
                    "amount_range": (8, 25),
                    "type": "expense",
                    "category": "Health",
                },
            ],
            "Utilities": [
                {
                    "description": "British Gas Bill",
                    "amount": 95.00,
                    "type": "expense",
                    "category": "Utilities",
                    "frequency": "monthly",
                    "day": 15,
                },
                {
                    "description": "Thames Water",
                    "amount": 35.00,
                    "type": "expense",
                    "category": "Utilities",
                    "frequency": "monthly",
                    "day": 10,
                },
                {
                    "description": "Virgin Media Broadband",
                    "amount": 45.00,
                    "type": "expense",
                    "category": "Utilities",
                    "frequency": "monthly",
                    "day": 8,
                },
            ],
            "Housing": [
                {
                    "description": "Rent Payment",
                    "amount": 1200.00,
                    "type": "expense",
                    "category": "Housing",
                    "frequency": "monthly",
                    "day": 1,
                },
            ],
        }

    except Exception as error:
        db.rollback()
        print(f"Error seeding demo transactions: {error}")

    finally:
        db.close()
