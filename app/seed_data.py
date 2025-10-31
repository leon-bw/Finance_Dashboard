from app.database import Session
from app.models import Category


def seed_default_categories():
    db = Session()

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

    for cat_data in default_categories:
        existing_category = (
            db.query(Category).filter(Category.name == cat_data["name"]).first()
        )
        if not existing_category:
            new_category = Category(**cat_data, is_default=True)
            db.add(new_category)

    db.commit()
    db.close()
    print("Default categories seeded successfully")
