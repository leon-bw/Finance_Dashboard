import random
from datetime import datetime, timedelta, timezone

from app.auth import get_password_hash

from .database import Session
from .models import (
    Category,
    Course,
    Lesson,
    Question,
    Transaction,
    Unit,
    User,
    UserLearningStats,
)


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
                "name": "Refunds",
                "type": "income",
                "description": "Money returned from a past purchase",
                "icon": "↩️",
                "colour": "#568203",  # darker green
            },
            {
                "name": "Gifts",
                "type": "income",
                "description": "Received as gifts from friends and family",
                "icon": "🎁",
                "colour": "#D1F6FF",  # light blue
            },
            {
                "name": "Bonus",
                "type": "income",
                "description": "Additional income awarded for performance",
                "icon": "🤑",
                "colour": "#EAA221",  # marigold
            },
            {
                "name": "Other",
                "type": "income",
                "description": "Other income",
                "icon": "💵",
                "colour": "#999999",  # light grey
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
                "name": "Savings",
                "type": "expense",
                "description": "Savings and emergency fund contributions",
                "icon": "🏦",
                "colour": "#FDFBD4",  # cream
            },
            {
                "name": "Debt Repayment",
                "type": "expense",
                "description": "Payment made toward an outstanding debt",
                "icon": "💳",
                "colour": "#6D3B07",  # mocha brown
            },
            {
                "name": "Charity",
                "type": "expense",
                "description": "Donation to a charitable cause",
                "icon": "❤️",
                "colour": "#FF0090",  # magenta
            },
            {
                "name": "Gifts",
                "type": "expense",
                "description": "Sent as gifts to friends and family",
                "icon": "🎁",
                "colour": "#111184",  # dark blue
            },
            {
                "name": "Other",
                "type": "expense",
                "description": "Other expenses",
                "icon": "💸",
                "colour": "#333333",  # dark grey
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
                email="demo@myfinancecoach.com",
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


def seed_demo_transactions():
    db = Session()

    try:
        demo_user = db.query(User).filter(User.is_demo).first()
        if not demo_user:
            print("Demo user not found, run seed_demo_user first")
            return

        demo_transactions = (
            db.query(Transaction).filter(Transaction.user_id == demo_user.id).count()
        )
        if demo_transactions > 0:
            print(
                f"Demo transactions already exist {demo_transactions} transactions in database"
            )
            return

        categories = {cat.name: cat for cat in db.query(Category).all()}

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
            "Savings": [
                {
                    "description": "Emergency Fund Contribution",
                    "amount": 150.00,
                    "type": "expense",
                    "category": "Savings",
                    "frequency": "monthly",
                    "day": 28,
                },
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
                    "amount_range": (3, 12),
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
            "Gifts": [
                {
                    "description": "Birthday Gift",
                    "amount_range": (20, 60),
                    "type": "expense",
                    "category": "Gifts",
                },
            ],
            "Charity": [
                {
                    "description": "Charity Donation",
                    "amount_range": (5, 30),
                    "type": "expense",
                    "category": "Charity",
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
            "Debt Repayment": [
                {
                    "description": "Credit Card Payment",
                    "amount_range": (50, 200),
                    "type": "expense",
                    "category": "Debt Repayment",
                },
            ],
            "Housing": [
                {
                    "description": "Mortgage Payment",
                    "amount": 1200.00,
                    "type": "expense",
                    "category": "Housing",
                    "frequency": "monthly",
                    "day": 1,
                },
            ],
        }

        end_date = datetime.now(timezone.utc)
        start_date = end_date - timedelta(days=90)

        transactions = []

        current_date = start_date
        while current_date <= end_date:
            for category_name, templates in transaction_template.items():
                for template in templates:
                    if template.get("frequency") == "monthly":
                        transaction_date = datetime(
                            current_date.year,
                            current_date.month,
                            template["day"],
                            random.randint(8, 22),
                            random.randint(0, 59),
                            tzinfo=timezone.utc,
                        )

                        if start_date <= transaction_date <= end_date:
                            category = categories.get(template["category"])
                            if category:
                                transactions.append(
                                    Transaction(
                                        user_id=demo_user.id,
                                        category_id=category.id,
                                        amount=template["amount"],
                                        description=template["description"],
                                        date=transaction_date,
                                        type=template["type"],
                                        account="Main Account",
                                        currency="GBP",
                                        status="completed",
                                    )
                                )

            if current_date.month == 12:
                current_date = datetime(
                    current_date.year + 1, 1, 1, tzinfo=timezone.utc
                )
            else:
                current_date = datetime(
                    current_date.year, current_date.month + 1, 1, tzinfo=timezone.utc
                )

        # Generate random one off transactions
        for category_name, templates in transaction_template.items():
            for template in templates:
                if template.get("frequency") != "monthly":
                    num_occurences = random.randint(1, 15)

                    for _ in range(num_occurences):
                        random_date = start_date + timedelta(
                            days=random.randint(0, 90),
                            hours=random.randint(8, 22),
                            minutes=random.randint(0, 59),
                        )

                        if "amount_range" in template:
                            amount = round(
                                random.uniform(
                                    template["amount_range"][0],
                                    template["amount_range"][1],
                                ),
                                2,
                            )
                        else:
                            amount = template["amount"]

                        category = categories.get(template["category"])
                        if category:
                            transactions.append(
                                Transaction(
                                    user_id=demo_user.id,
                                    category_id=category.id,
                                    amount=amount,
                                    description=template["description"],
                                    date=random_date,
                                    type=template["type"],
                                    account="Main Account",
                                    currency="GBP",
                                    status="completed",
                                )
                            )

        db.bulk_save_objects(transactions)
        db.commit()

        total_income = sum(t.amount for t in transactions if t.type == "income")
        total_expenses = sum(t.amount for t in transactions if t.type == "expense")

        print(f"Demo transactions created: {len(transactions)} transactions")
        print(f"Total Income: £{total_income:,.2f}")
        print(f"Total Expenses: £{total_expenses:,.2f}")

    except Exception as error:
        db.rollback()
        print(f"Error seeding demo transactions: {error}")

    finally:
        db.close()


LEARNING_CONTENT = {
    "slug": "budgeting-basics",
    "title": "Budgeting Basics",
    "description": "Learn the fundamentals of budgeting and take control of your money.",
    "icon": "📘",
    "colour": "#58CC02",  # Duolingo green
    "order": 1,
    "units": [
        {
            "title": "Getting Started",
            "description": "What a budget is and why it matters.",
            "order": 1,
            "lessons": [
                {
                    "title": "What is a budget?",
                    "order": 1,
                    "xp_reward": 10,
                    "questions": [
                        {
                            "prompt": "What is a budget?",
                            "type": "multiple_choice",
                            "options": [
                                "A plan for how you spend and save your money",
                                "A type of bank account",
                                "A government tax",
                                "A credit score",
                            ],
                            "correct_answer": "A plan for how you spend and save your money",
                            "explanation": "A budget is simply a plan that helps you decide how to use your income.",
                            "order": 1,
                        },
                        {
                            "prompt": "A budget can help you avoid overspending.",
                            "type": "true_false",
                            "options": ["True", "False"],
                            "correct_answer": "True",
                            "explanation": "By planning ahead, a budget helps you keep spending under control.",
                            "order": 2,
                        },
                        {
                            "prompt": "Which of these is the first step in making a budget?",
                            "type": "multiple_choice",
                            "options": [
                                "Know your income",
                                "Cancel all subscriptions",
                                "Open a new credit card",
                                "Sell your car",
                            ],
                            "correct_answer": "Know your income",
                            "explanation": "You need to know how much money is coming in before you can plan how to use it.",
                            "order": 3,
                        },
                    ],
                },
                {
                    "title": "Needs vs wants",
                    "order": 2,
                    "xp_reward": 10,
                    "questions": [
                        {
                            "prompt": "Which of these is a 'need'?",
                            "type": "multiple_choice",
                            "options": [
                                "Rent",
                                "A holiday abroad",
                                "A new games console",
                                "Designer trainers",
                            ],
                            "correct_answer": "Rent",
                            "explanation": "Needs are essentials like housing, food and utilities.",
                            "order": 1,
                        },
                        {
                            "prompt": "A streaming subscription is usually a 'want', not a 'need'.",
                            "type": "true_false",
                            "options": ["True", "False"],
                            "correct_answer": "True",
                            "explanation": "Entertainment is nice to have, but it is not essential for living.",
                            "order": 2,
                        },
                    ],
                },
            ],
        },
        {
            "title": "Saving Smart",
            "description": "Build habits that grow your savings.",
            "order": 2,
            "lessons": [
                {
                    "title": "The 50/30/20 rule",
                    "order": 1,
                    "xp_reward": 15,
                    "questions": [
                        {
                            "prompt": "In the 50/30/20 rule, what does the 20% represent?",
                            "type": "multiple_choice",
                            "options": [
                                "Savings and debt repayment",
                                "Needs",
                                "Wants",
                                "Taxes",
                            ],
                            "correct_answer": "Savings and debt repayment",
                            "explanation": "50% goes to needs, 30% to wants, and 20% to savings and paying off debt.",
                            "order": 1,
                        },
                        {
                            "prompt": "The 50/30/20 rule suggests spending 50% of income on wants.",
                            "type": "true_false",
                            "options": ["True", "False"],
                            "correct_answer": "False",
                            "explanation": "50% is for needs, not wants. Wants get 30%.",
                            "order": 2,
                        },
                        {
                            "prompt": "Why is an emergency fund important?",
                            "type": "multiple_choice",
                            "options": [
                                "It covers unexpected costs without going into debt",
                                "It increases your tax bill",
                                "It lowers your salary",
                                "It is required by law",
                            ],
                            "correct_answer": "It covers unexpected costs without going into debt",
                            "explanation": "An emergency fund is a safety net for surprises like a car repair or job loss.",
                            "order": 3,
                        },
                    ],
                },
            ],
        },
    ],
}


def seed_learning_content():
    db = Session()

    try:
        existing = (
            db.query(Course).filter(Course.slug == LEARNING_CONTENT["slug"]).first()
        )
        if existing:
            print("Learning content already exists")
        else:
            course = Course(
                title=LEARNING_CONTENT["title"],
                slug=LEARNING_CONTENT["slug"],
                description=LEARNING_CONTENT["description"],
                icon=LEARNING_CONTENT["icon"],
                colour=LEARNING_CONTENT["colour"],
                order=LEARNING_CONTENT["order"],
            )
            db.add(course)
            db.flush()  # assign course.id before adding units

            lesson_count = 0
            question_count = 0
            for unit_data in LEARNING_CONTENT["units"]:
                unit = Unit(
                    course_id=course.id,
                    title=unit_data["title"],
                    description=unit_data["description"],
                    order=unit_data["order"],
                )
                db.add(unit)
                db.flush()

                for lesson_data in unit_data["lessons"]:
                    lesson = Lesson(
                        unit_id=unit.id,
                        title=lesson_data["title"],
                        order=lesson_data["order"],
                        xp_reward=lesson_data["xp_reward"],
                    )
                    db.add(lesson)
                    db.flush()
                    lesson_count += 1

                    for question_data in lesson_data["questions"]:
                        db.add(
                            Question(
                                lesson_id=lesson.id,
                                prompt=question_data["prompt"],
                                type=question_data["type"],
                                options=question_data["options"],
                                correct_answer=question_data["correct_answer"],
                                explanation=question_data["explanation"],
                                order=question_data["order"],
                            )
                        )
                        question_count += 1

            db.commit()
            print(
                f"Learning content created: 1 course, {lesson_count} lessons, "
                f"{question_count} questions"
            )

        # Make sure the demo user has a learning stats record
        demo_user = db.query(User).filter(User.is_demo).first()
        if demo_user:
            stats = (
                db.query(UserLearningStats)
                .filter(UserLearningStats.user_id == demo_user.id)
                .first()
            )
            if not stats:
                db.add(UserLearningStats(user_id=demo_user.id))
                db.commit()
                print("Learning stats created for demo user")

    except Exception as error:
        db.rollback()
        print(f"Error seeding learning content: {error}")

    finally:
        db.close()


def seed_all():
    print("started database seeding")
    seed_default_categories()
    seed_demo_user()
    seed_demo_transactions()
    seed_learning_content()
    print("Database seeding complete")


if __name__ == "__main__":
    seed_all()
