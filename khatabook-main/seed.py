"""
Seed the database with a demo shopkeeper account and sample customers/transactions.
Run with: python seed.py
"""
import random
from datetime import datetime, timedelta

from app import app
from models import db, User, Customer, Transaction

DEMO_EMAIL = "demo@khatabook.local"
DEMO_PASSWORD = "demo1234"

CUSTOMERS = [
    {"name": "Ahmed Traders", "phone": "03211112222"},
    {"name": "Fatima Bibi", "phone": "03331113333"},
    {"name": "Malik Kirana Store", "phone": "03451114444"},
    {"name": "Bilal Auto Parts", "phone": "03011115555"},
    {"name": "Sana Bakers", "phone": "03211116666"},
    {"name": "Imran Hardware", "phone": None},
]

NOTES_CREDIT = ["flour 2 bags", "cash advance", "cement 5 bags", "sugar & rice", "cooking oil", None]
NOTES_DEBIT = ["cash payment", "partial payment", "bank transfer", "cheque cleared", None]


def seed():
    with app.app_context():
        db.create_all()

        if User.query.filter_by(email=DEMO_EMAIL).first():
            print("Demo data already exists — skipping.")
            return

        user = User(business_name="Ali General Store", email=DEMO_EMAIL, email_verified=True)
        user.set_password(DEMO_PASSWORD)
        db.session.add(user)
        db.session.flush()

        today = datetime.utcnow()
        for c in CUSTOMERS:
            customer = Customer(user_id=user.id, name=c["name"], phone=c["phone"])
            db.session.add(customer)
            db.session.flush()

            num_tx = random.randint(3, 8)
            day_offset = random.randint(1, 45)
            for _ in range(num_tx):
                day_offset -= random.randint(1, 6)
                tx_date = today - timedelta(days=max(day_offset, 0), hours=random.randint(0, 23))
                tx_type = random.choices(["credit", "debit"], weights=[0.6, 0.4])[0]
                amount = random.choice([500, 750, 1000, 1500, 2200, 3000, 5000, 8000]) * 100
                note = random.choice(NOTES_CREDIT if tx_type == "credit" else NOTES_DEBIT)

                db.session.add(Transaction(
                    customer_id=customer.id,
                    type=tx_type,
                    amount_paisa=amount,
                    note=note,
                    date=tx_date,
                    created_by=user.id,
                ))

        db.session.commit()
        print("Seeded demo account:")
        print(f"  Email:    {DEMO_EMAIL}")
        print(f"  Password: {DEMO_PASSWORD}")


if __name__ == "__main__":
    seed()
