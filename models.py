from datetime import datetime, date, timedelta
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()


class User(UserMixin, db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    business_name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    theme = db.Column(db.String(10), nullable=False, default="light")  # 'light' | 'dark'
    currency = db.Column(db.String(3), nullable=False, default="INR")  # ISO 4217 code
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    email_verified = db.Column(db.Boolean, nullable=False, default=False)
    otp_code_hash = db.Column(db.String(255), nullable=True)
    otp_purpose = db.Column(db.String(20), nullable=True)  # 'register' | 'login'
    otp_expires_at = db.Column(db.DateTime, nullable=True)
    otp_attempts = db.Column(db.Integer, nullable=False, default=0)

    is_premium = db.Column(db.Boolean, nullable=False, default=False)
    premium_since = db.Column(db.DateTime, nullable=True)
    premium_plan = db.Column(db.String(20), nullable=True)  # 'monthly' | 'yearly'

    customers = db.relationship(
        "Customer", backref="owner", lazy=True, cascade="all, delete-orphan"
    )
    payments = db.relationship(
        "Payment", backref="user", lazy=True, cascade="all, delete-orphan"
    )

    def set_password(self, raw_password):
        self.password_hash = generate_password_hash(raw_password)

    def check_password(self, raw_password):
        return check_password_hash(self.password_hash, raw_password)

    def set_otp(self, code, purpose, ttl_minutes=10):
        self.otp_code_hash = generate_password_hash(code)
        self.otp_purpose = purpose
        self.otp_expires_at = datetime.utcnow() + timedelta(minutes=ttl_minutes)
        self.otp_attempts = 0

    def check_otp(self, code, purpose):
        if not self.otp_code_hash or self.otp_purpose != purpose:
            return False
        if not self.otp_expires_at or datetime.utcnow() > self.otp_expires_at:
            return False
        if self.otp_attempts >= 5:
            return False
        ok = check_password_hash(self.otp_code_hash, code)
        if not ok:
            self.otp_attempts = (self.otp_attempts or 0) + 1
        return ok

    def clear_otp(self):
        self.otp_code_hash = None
        self.otp_purpose = None
        self.otp_expires_at = None
        self.otp_attempts = 0


class Customer(db.Model):
    __tablename__ = "customers"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    name = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(20), nullable=True)
    photo = db.Column(db.String(255), nullable=True)  # optional path/emoji/initial color seed
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    transactions = db.relationship(
        "Transaction", backref="customer", lazy=True, cascade="all, delete-orphan",
        order_by="Transaction.date, Transaction.id"
    )
    reminders = db.relationship(
        "Reminder", backref="customer", lazy=True, cascade="all, delete-orphan"
    )

    @property
    def balance_paisa(self):
        """Positive = customer owes shopkeeper (You'll Get). Negative = shopkeeper owes customer (You'll Give)."""
        credit = sum(t.amount_paisa for t in self.transactions if t.type == "credit")
        debit = sum(t.amount_paisa for t in self.transactions if t.type == "debit")
        return credit - debit

    @property
    def balance_rupees(self):
        return self.balance_paisa / 100.0

    @property
    def last_transaction_date(self):
        if not self.transactions:
            return self.created_at
        return max(t.date for t in self.transactions)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "phone": self.phone,
            "photo": self.photo,
            "balance_paisa": self.balance_paisa,
            "balance_rupees": self.balance_rupees,
            "last_transaction_date": self.last_transaction_date.isoformat(),
        }


class Transaction(db.Model):
    __tablename__ = "transactions"

    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey("customers.id"), nullable=False, index=True)
    type = db.Column(db.String(10), nullable=False)  # 'credit' (they owe you) | 'debit' (they paid back)
    amount_paisa = db.Column(db.Integer, nullable=False)  # store in paisa/cents, integer only
    note = db.Column(db.String(255), nullable=True)
    date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    created_by = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    @property
    def amount_rupees(self):
        return self.amount_paisa / 100.0

    def to_dict(self):
        return {
            "id": self.id,
            "customer_id": self.customer_id,
            "type": self.type,
            "amount_paisa": self.amount_paisa,
            "amount_rupees": self.amount_rupees,
            "note": self.note,
            "date": self.date.isoformat(),
        }


class Payment(db.Model):
    __tablename__ = "payments"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    plan = db.Column(db.String(20), nullable=False)  # 'monthly' | 'yearly'
    amount_paisa = db.Column(db.Integer, nullable=False)
    currency = db.Column(db.String(3), nullable=False, default="INR")
    razorpay_order_id = db.Column(db.String(64), unique=True, nullable=False, index=True)
    razorpay_payment_id = db.Column(db.String(64), nullable=True)
    razorpay_signature = db.Column(db.String(255), nullable=True)
    status = db.Column(db.String(10), nullable=False, default="created")  # created | paid | failed
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    paid_at = db.Column(db.DateTime, nullable=True)


class Reminder(db.Model):
    __tablename__ = "reminders"

    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey("customers.id"), nullable=False, index=True)
    scheduled_date = db.Column(db.Date, nullable=False, default=date.today)
    message = db.Column(db.String(500), nullable=False)
    status = db.Column(db.String(10), nullable=False, default="pending")  # pending | sent
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
