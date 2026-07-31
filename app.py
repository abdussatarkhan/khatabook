import csv
import io
import json
import os
from datetime import datetime, date, timedelta

from flask import (
    Flask, render_template, request, redirect, url_for, flash,
    jsonify, Response, send_file
)
from flask_login import (
    LoginManager, login_user, logout_user, login_required, current_user
)
from flask_wtf import CSRFProtect

from models import db, User, Customer, Transaction, Reminder
from currencies import CURRENCIES, DEFAULT_CURRENCY, currency_symbol, currency_locale

app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "dev-secret-key-change-in-production")
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL", "sqlite:///khatabook.db")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)
csrf = CSRFProtect(app)

login_manager = LoginManager(app)
login_manager.login_view = "login"
login_manager.login_message = "Please log in to continue."


@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def rupees_to_paisa(value):
    """Convert a rupee amount (string/float) to an integer paisa value safely."""
    try:
        rupees = round(float(value), 2)
    except (TypeError, ValueError):
        raise ValueError("Invalid amount")
    if rupees <= 0:
        raise ValueError("Amount must be greater than zero")
    return int(round(rupees * 100))


def paisa_to_rupees(paisa):
    return round(paisa / 100.0, 2)


def customer_summary(c: Customer):
    bal = c.balance_paisa
    return {
        "id": c.id,
        "name": c.name,
        "phone": c.phone,
        "balance_paisa": bal,
        "balance_rupees": paisa_to_rupees(bal),
        "direction": "get" if bal > 0 else ("give" if bal < 0 else "settled"),
        "last_transaction_date": c.last_transaction_date.isoformat(),
    }


# ---------------------------------------------------------------------------
# Auth
# ---------------------------------------------------------------------------

@app.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard"))

    if request.method == "POST":
        business_name = request.form.get("business_name", "").strip()
        phone = request.form.get("phone", "").strip()
        password = request.form.get("password", "")

        error = None
        if not business_name:
            error = "Business name is required."
        elif not phone:
            error = "Phone number is required."
        elif len(password) < 4:
            error = "Password must be at least 4 characters."
        elif User.query.filter_by(phone=phone).first():
            error = "An account with this phone number already exists."

        if error:
            flash(error, "error")
            return render_template("register.html", business_name=business_name, phone=phone)

        user = User(business_name=business_name, phone=phone)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        login_user(user)
        flash("Account created. Welcome!", "success")
        return redirect(url_for("dashboard"))

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard"))

    if request.method == "POST":
        phone = request.form.get("phone", "").strip()
        password = request.form.get("password", "")
        user = User.query.filter_by(phone=phone).first()

        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for("dashboard"))

        flash("Incorrect phone number or password.", "error")
        return render_template("login.html", phone=phone)

    return render_template("login.html")


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("login"))


# ---------------------------------------------------------------------------
# Dashboard
# ---------------------------------------------------------------------------

@app.route("/")
@login_required
def dashboard():
    customers = Customer.query.filter_by(user_id=current_user.id).all()
    customers.sort(key=lambda c: c.last_transaction_date, reverse=True)

    summaries = [customer_summary(c) for c in customers]
    youll_get = sum(s["balance_rupees"] for s in summaries if s["balance_rupees"] > 0)
    youll_give = sum(-s["balance_rupees"] for s in summaries if s["balance_rupees"] < 0)

    return render_template(
        "dashboard.html",
        customers=summaries,
        youll_get=round(youll_get, 2),
        youll_give=round(youll_give, 2),
    )


# ---------------------------------------------------------------------------
# Customers (API)
# ---------------------------------------------------------------------------

@app.route("/api/customers", methods=["POST"])
@login_required
def create_customer():
    data = request.get_json(silent=True) or request.form
    name = (data.get("name") or "").strip()
    phone = (data.get("phone") or "").strip()

    if not name:
        return jsonify({"error": "Name is required."}), 400

    customer = Customer(user_id=current_user.id, name=name, phone=phone or None)
    db.session.add(customer)
    db.session.commit()

    return jsonify({"id": customer.id, "name": customer.name, "phone": customer.phone}), 201


@app.route("/api/customers/search")
@login_required
def search_customers():
    q = (request.args.get("q") or "").strip()
    query = Customer.query.filter_by(user_id=current_user.id)
    if q:
        query = query.filter(Customer.name.ilike(f"%{q}%"))
    customers = query.all()
    customers.sort(key=lambda c: c.last_transaction_date, reverse=True)
    return jsonify([c.to_dict() for c in customers])


@app.route("/customer/<int:customer_id>")
@login_required
def customer_detail(customer_id):
    customer = Customer.query.filter_by(id=customer_id, user_id=current_user.id).first_or_404()
    transactions = sorted(customer.transactions, key=lambda t: (t.date, t.id))
    return render_template("customer_detail.html", customer=customer, transactions=transactions)


@app.route("/api/customers/<int:customer_id>", methods=["DELETE"])
@login_required
def delete_customer(customer_id):
    customer = Customer.query.filter_by(id=customer_id, user_id=current_user.id).first_or_404()
    db.session.delete(customer)
    db.session.commit()
    return jsonify({"ok": True})


# ---------------------------------------------------------------------------
# Transactions (API)
# ---------------------------------------------------------------------------

@app.route("/api/customers/<int:customer_id>/transactions", methods=["POST"])
@login_required
def add_transaction(customer_id):
    customer = Customer.query.filter_by(id=customer_id, user_id=current_user.id).first_or_404()
    data = request.get_json(silent=True) or request.form

    tx_type = data.get("type")
    if tx_type not in ("credit", "debit"):
        return jsonify({"error": "Invalid transaction type."}), 400

    try:
        amount_paisa = rupees_to_paisa(data.get("amount"))
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400

    note = (data.get("note") or "").strip()[:255]
    date_str = data.get("date")
    try:
        tx_date = datetime.strptime(date_str, "%Y-%m-%d") if date_str else datetime.utcnow()
    except ValueError:
        tx_date = datetime.utcnow()

    tx = Transaction(
        customer_id=customer.id,
        type=tx_type,
        amount_paisa=amount_paisa,
        note=note or None,
        date=tx_date,
        created_by=current_user.id,
    )
    db.session.add(tx)
    db.session.commit()

    return jsonify({
        "id": tx.id,
        "type": tx.type,
        "amount_rupees": paisa_to_rupees(tx.amount_paisa),
        "note": tx.note,
        "date": tx.date.strftime("%d %b %Y, %I:%M %p"),
        "new_balance_rupees": paisa_to_rupees(customer.balance_paisa),
    }), 201


@app.route("/api/transactions/<int:tx_id>", methods=["DELETE"])
@login_required
def delete_transaction(tx_id):
    tx = Transaction.query.get_or_404(tx_id)
    customer = Customer.query.filter_by(id=tx.customer_id, user_id=current_user.id).first_or_404()
    db.session.delete(tx)
    db.session.commit()
    return jsonify({"ok": True, "new_balance_rupees": paisa_to_rupees(customer.balance_paisa)})


# ---------------------------------------------------------------------------
# Reminders
# ---------------------------------------------------------------------------

@app.route("/api/customers/<int:customer_id>/reminder", methods=["POST"])
@login_required
def send_reminder(customer_id):
    customer = Customer.query.filter_by(id=customer_id, user_id=current_user.id).first_or_404()
    bal = paisa_to_rupees(customer.balance_paisa)
    symbol = currency_symbol(current_user.currency or DEFAULT_CURRENCY)

    if bal > 0:
        message = (
            f"Namaste {customer.name}, this is a reminder from {current_user.business_name}. "
            f"Your outstanding balance is {symbol}{bal:,.2f}. Please clear it at your convenience. Thank you!"
        )
    elif bal < 0:
        message = (
            f"Hi {customer.name}, note from {current_user.business_name}: "
            f"we owe you {symbol}{abs(bal):,.2f}. We'll settle it soon. Thank you!"
        )
    else:
        message = f"Hi {customer.name}, your account with {current_user.business_name} is fully settled. Thank you!"

    reminder = Reminder(customer_id=customer.id, message=message, status="sent")
    db.session.add(reminder)
    db.session.commit()

    phone_digits = "".join(ch for ch in (customer.phone or "") if ch.isdigit())
    wa_link = f"https://wa.me/{phone_digits}?text={message}"

    return jsonify({"message": message, "wa_link": wa_link, "has_phone": bool(phone_digits)})


# ---------------------------------------------------------------------------
# Reports
# ---------------------------------------------------------------------------

@app.route("/reports")
@login_required
def reports():
    return render_template("reports.html")


@app.route("/api/reports/data")
@login_required
def reports_data():
    start_str = request.args.get("start")
    end_str = request.args.get("end")

    today = date.today()
    start = datetime.strptime(start_str, "%Y-%m-%d") if start_str else datetime.combine(today - timedelta(days=29), datetime.min.time())
    end = datetime.strptime(end_str, "%Y-%m-%d") if end_str else datetime.combine(today, datetime.min.time())
    end = end + timedelta(days=1)  # inclusive of end date

    customer_ids = [c.id for c in Customer.query.filter_by(user_id=current_user.id).all()]
    txs = Transaction.query.filter(
        Transaction.customer_id.in_(customer_ids),
        Transaction.date >= start,
        Transaction.date < end,
    ).order_by(Transaction.date).all()

    by_day = {}
    total_credit = 0
    total_debit = 0
    for t in txs:
        day = t.date.strftime("%Y-%m-%d")
        by_day.setdefault(day, {"credit": 0, "debit": 0})
        by_day[day][t.type] += t.amount_paisa
        if t.type == "credit":
            total_credit += t.amount_paisa
        else:
            total_debit += t.amount_paisa

    labels = sorted(by_day.keys())
    return jsonify({
        "labels": labels,
        "credit": [paisa_to_rupees(by_day[d]["credit"]) for d in labels],
        "debit": [paisa_to_rupees(by_day[d]["debit"]) for d in labels],
        "total_credit": paisa_to_rupees(total_credit),
        "total_debit": paisa_to_rupees(total_debit),
        "transaction_count": len(txs),
    })


@app.route("/reports/export.csv")
@login_required
def export_csv():
    customers = Customer.query.filter_by(user_id=current_user.id).all()
    output = io.StringIO()
    writer = csv.writer(output)
    currency_code = current_user.currency or DEFAULT_CURRENCY
    writer.writerow(["Customer", "Phone", "Date", "Type", f"Amount ({currency_code})", "Note"])
    for c in customers:
        for t in sorted(c.transactions, key=lambda t: t.date):
            writer.writerow([
                c.name, c.phone or "", t.date.strftime("%Y-%m-%d %H:%M"),
                "You Gave" if t.type == "credit" else "You Got",
                f"{paisa_to_rupees(t.amount_paisa):.2f}", t.note or "",
            ])

    mem = io.BytesIO(output.getvalue().encode("utf-8"))
    return send_file(
        mem, mimetype="text/csv", as_attachment=True,
        download_name=f"khatabook-export-{date.today().isoformat()}.csv",
    )


# ---------------------------------------------------------------------------
# Settings
# ---------------------------------------------------------------------------

@app.route("/settings", methods=["GET", "POST"])
@login_required
def settings():
    if request.method == "POST":
        business_name = request.form.get("business_name", "").strip()
        phone = request.form.get("phone", "").strip()
        if business_name:
            current_user.business_name = business_name
        if phone:
            current_user.phone = phone
        db.session.commit()
        flash("Settings updated.", "success")
        return redirect(url_for("settings"))

    return render_template("settings.html")


@app.route("/settings/export.json")
@login_required
def export_json():
    customers = Customer.query.filter_by(user_id=current_user.id).all()
    data = {
        "business_name": current_user.business_name,
        "phone": current_user.phone,
        "exported_at": datetime.utcnow().isoformat(),
        "customers": [],
    }
    for c in customers:
        data["customers"].append({
            "name": c.name,
            "phone": c.phone,
            "created_at": c.created_at.isoformat(),
            "transactions": [
                {
                    "type": t.type,
                    "amount_rupees": paisa_to_rupees(t.amount_paisa),
                    "note": t.note,
                    "date": t.date.isoformat(),
                }
                for t in c.transactions
            ],
        })

    mem = io.BytesIO(json.dumps(data, indent=2).encode("utf-8"))
    return send_file(
        mem, mimetype="application/json", as_attachment=True,
        download_name=f"khatabook-backup-{date.today().isoformat()}.json",
    )


# ---------------------------------------------------------------------------
# PWA
# ---------------------------------------------------------------------------

@app.route("/offline")
def offline():
    return render_template("offline.html")


@app.route("/.well-known/assetlinks.json")
def assetlinks():
    return send_file(
        os.path.join(app.root_path, "static", ".well-known", "assetlinks.json"),
        mimetype="application/json",
    )


@app.context_processor
def inject_globals():
    if current_user.is_authenticated:
        theme = current_user.theme or "light"
        code = current_user.currency or DEFAULT_CURRENCY
    else:
        theme = "light"
        code = DEFAULT_CURRENCY
    return {
        "now": datetime.utcnow(),
        "current_theme": theme,
        "current_currency_code": code,
        "current_currency_symbol": currency_symbol(code),
        "current_currency_locale": currency_locale(code),
        "currencies": CURRENCIES,
    }


# ---------------------------------------------------------------------------
# Preferences (theme + currency) — instant AJAX save
# ---------------------------------------------------------------------------

@app.route("/api/preferences", methods=["POST"])
@login_required
def update_preferences():
    data = request.get_json(silent=True) or request.form

    theme = data.get("theme")
    currency = data.get("currency")

    if theme is not None:
        if theme not in ("light", "dark"):
            return jsonify({"error": "Invalid theme."}), 400
        current_user.theme = theme

    if currency is not None:
        if currency not in CURRENCIES:
            return jsonify({"error": "Unsupported currency."}), 400
        current_user.currency = currency

    db.session.commit()

    return jsonify({
        "ok": True,
        "theme": current_user.theme,
        "currency": current_user.currency,
        "currency_symbol": currency_symbol(current_user.currency),
        "currency_locale": currency_locale(current_user.currency),
    })


def _migrate_new_columns():
    """Add theme/currency columns to an existing pre-upgrade sqlite db, if needed."""
    from sqlalchemy import inspect, text

    inspector = inspect(db.engine)
    if "users" not in inspector.get_table_names():
        return
    existing_cols = {c["name"] for c in inspector.get_columns("users")}
    with db.engine.begin() as conn:
        if "theme" not in existing_cols:
            conn.execute(text("ALTER TABLE users ADD COLUMN theme VARCHAR(10) DEFAULT 'light'"))
        if "currency" not in existing_cols:
            conn.execute(text("ALTER TABLE users ADD COLUMN currency VARCHAR(3) DEFAULT 'INR'"))


# Ensure tables (and any new columns) exist regardless of how the app is
# started — `python app.py`, `flask run`, or a production WSGI server all
# import this module, so this must not be gated behind `__main__`.
with app.app_context():
    db.create_all()
    _migrate_new_columns()


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
