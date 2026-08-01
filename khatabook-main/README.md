# Khatabook — Digital Udhaar Ledger

A mobile-installable Flask PWA for shopkeepers to track customer credit (udhaar): who owes you, who you owe, and to send payment reminders. Works offline for pages you've already opened, and installs to your phone's home screen like a native app.

## Features

- **Email-verified accounts & 2-step login** — sign up with your Gmail (or any email), confirm it with a 6-digit code, and every login sends a fresh code to your email before you're let in. Passwords have a Show/Hide toggle.
- **PDF customer statements** — download a polished PDF ledger for any customer (business name, transaction history, running balance) from their profile page.
- **Light/dark theme** — toggle from the floating button on any screen or the switch in Settings. Saved per account and synced across devices; falls back to your device's system preference before you log in.
- **Multi-currency support** — pick your currency (₹ INR, ₨ PKR, $ USD, € EUR, £ GBP, and ~35 others) in Settings; every amount, chart, CSV export, and WhatsApp reminder message updates instantly.
- Phone + password login for shopkeepers
- Dashboard with "You'll get" / "You'll give" totals, customer search, and a sorted customer list
- Per-customer ledger thread ("You gave" / "You got" entries, running balance)
- One-tap WhatsApp reminder links (`wa.me`) with an auto-generated message
- Reports page with a Chart.js credit-vs-debit trend and CSV export
- Settings page with a full JSON backup of your data
- Installable PWA with offline caching of the app shell
- Server-side customer search API (`/api/customers/search`) for scaling past the in-page filter

## Setup

```bash
cd khatabook
pip install -r requirements.txt

# Optional: create a demo shopkeeper with sample customers/transactions
python seed.py

flask run
```

Then open **http://127.0.0.1:5000** in your browser.

If you ran `seed.py`, log in with:

- **Phone:** `03001234567`
- **Password:** `demo1234`

Otherwise, tap **Create an account** on the login screen to set up your own shop.

The database is a single SQLite file created automatically at `instance/khatabook.db` the first time the app runs (Flask's default instance-folder location) — there's nothing else to configure.

## Installing it as an app on your phone

**Android (Chrome):**
1. Open the site's URL in Chrome on your phone.
2. Tap the **⋮** menu → **Add to Home screen** (Chrome may also show an automatic "Install app" prompt/banner).
3. Confirm — the Khatabook icon now appears on your home screen and opens full-screen, like a native app.

**iPhone (Safari):**
1. Open the site's URL in Safari.
2. Tap the **Share** icon → **Add to Home Screen**.
3. Confirm — it now opens full-screen from your home screen.

**Desktop (Chrome/Edge):** click the install icon (⊕) in the address bar, or the browser's "Install app" menu item.

To verify installability yourself: open Chrome DevTools → **Application** tab → **Manifest**, and check there are no errors listed.

## Project structure

```
khatabook/
├── app.py                 # Flask routes, auth, API endpoints
├── models.py               # SQLAlchemy models (User, Customer, Transaction, Reminder)
├── seed.py                 # Demo data seeder
├── requirements.txt
├── templates/               # Jinja2 page templates
│   ├── base.html            # Shared shell: bottom nav, manifest link, SW registration
│   ├── login.html / register.html
│   ├── dashboard.html
│   ├── customer_detail.html
│   ├── reports.html
│   ├── settings.html
│   └── offline.html         # Offline fallback page
└── static/
    ├── css/style.css
    ├── js/app.js             # Dashboard: search, add-customer sheet
    ├── js/customer.js        # Ledger: add-transaction sheet, reminders
    ├── js/reports.js         # Chart.js trend chart, date range
    ├── manifest.json
    ├── sw.js                 # Service worker (offline app-shell caching)
    └── icons/                # App icons (192px, 512px, maskable)
```

## Notes on money handling

All amounts are stored as **integer paisa** (`amount_paisa`) in the database — never floats — to avoid rounding errors. Conversion to/from rupees for display and input happens only at the API/template boundary (`rupees_to_paisa` / `paisa_to_rupees` in `app.py`).

## What's out of scope (v1)

- Real SMS/WhatsApp Business API integration — reminders use free `wa.me` deep links instead
- Multi-user/staff accounts per shop
- Cloud sync across multiple devices (SQLite is local to the machine running the server)

## A note on production use

The built-in `flask run` server is for development only. To actually deploy this (e.g. so a shopkeeper can reach it from their phone over the internet), run it behind a production WSGI server such as **gunicorn** or **waitress**, and change `SECRET_KEY` in `app.py` to a real secret loaded from an environment variable.

## Setting up email sending (required for signup/login codes)

This app sends verification codes by email using SMTP. Without these environment variables set, the app still works for testing — it will show the code directly on screen instead of emailing it — but for real use you need to configure a real mail sender.

**Using Gmail:**
1. Turn on 2-Step Verification on the Gmail account you want to send from: https://myaccount.google.com/security
2. Create an "App Password": https://myaccount.google.com/apppasswords (choose "Mail" as the app)
3. Set these environment variables wherever you deploy (e.g. Render → your service → Environment):
   - `SMTP_HOST` = `smtp.gmail.com`
   - `SMTP_PORT` = `587`
   - `SMTP_USER` = your full Gmail address
   - `SMTP_PASS` = the 16-character App Password (not your normal Gmail password)
   - `MAIL_FROM` = same as `SMTP_USER` (optional, defaults to it)

Any other SMTP provider (SendGrid, Mailgun, your own mail server, etc.) works the same way — just point `SMTP_HOST`/`SMTP_PORT`/`SMTP_USER`/`SMTP_PASS` at it.
