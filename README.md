# KhataBook — Digital Ledger & Merchant Cashbook Application

<div align="center">

[![Daily Streak](https://img.shields.io/badge/Daily%20Streak-Active%20%F0%9F%94%A5-brightgreen?style=flat-square&logo=github)](https://github.com/abdussatarkhan)
[![Software Portfolio](https://img.shields.io/badge/Portfolio-Software%20Engineering%20%26%20Systems-0e75b6?style=flat-square&logo=github)](https://github.com/abdussatarkhan)
[![Author: Abdussatar](https://img.shields.io/badge/Author-Abdussatar-24292e?style=flat-square&logo=github)](https://github.com/abdussatarkhan)

</div>

[![CI](https://github.com/abdussatarkhan/khatabook/actions/workflows/ci.yml/badge.svg)](https://github.com/abdussatarkhan/khatabook/actions)
[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-2.x-000000?style=for-the-badge&logo=flask&logoColor=white)](https://flask.palletsprojects.com/)
[![SQLite](https://img.shields.io/badge/SQLite-Local_Storage-07405E?style=for-the-badge&logo=sqlite&logoColor=white)](https://www.sqlite.org/)
[![PWA](https://img.shields.io/badge/PWA-Mobile_Ready-5A0FC8?style=for-the-badge&logo=pwa&logoColor=white)](https://web.dev/progressive-web-apps/)

> **A mobile-first digital accounting ledger and customer credit manager designed for small business shopkeepers built with Python Flask and SQLite, featuring Progressive Web App (PWA) offline capabilities — managing customer debit/credit transactions (Udhar), automated balance reminders, and daily cash flow reconciliation.**

---

## 🏛️ System Architecture

```mermaid
graph TD
    Client[Merchant Mobile / Browser PWA UI] --> FlaskApp[Flask Web Routing & Auth]
    FlaskApp --> LedgerEngine[Debit & Credit Accounting Engine]
    LedgerEngine --> DB[(SQLite Database: Customers, Transactions, Logs)]
    LedgerEngine --> Notifier[WhatsApp / SMS Reminder Notification Formatter]
    LedgerEngine --> Export[Daily P&L & Cash Summary Exporter]
```

---

## 🌟 Key Features & Capabilities

- **📒 Digital Udhar & Credit Ledger**: Replaces traditional manual paper registers with an organized digital debit/credit ledger for each customer and supplier.
- **💵 Real-Time Cash Flow Reconciliation**: Instantly computes total amount receivable (You'll Receive / Lene Hain) vs amount payable (You'll Give / Dene Hain) with net daily cash balances.
- **📱 Progressive Web App (PWA) Enabled**: Includes `sw.js` service worker and `manifest.json` for installable mobile home-screen access and offline asset caching.
- **📩 Automated Payment Reminders**: Generates pre-formatted WhatsApp and SMS reminder links containing exact due balances and payment details.

---

## 🚀 Quickstart & Setup

### Prerequisites
- [Python 3.10+](https://www.python.org/downloads/)

### 1. Clone the Repository
```bash
git clone https://github.com/abdussatarkhan/khatabook.git
cd khatabook
```

### 2. Environment Setup & Run
```bash
# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: .\venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the Flask application
python app.py
```

Open your browser and navigate to:
`http://localhost:5000`

---

## 🖥️ Application & Operational Interface

<p align="center">
  <img src="screenshots/01_dashboard_preview.png" alt="KhataBook Merchant Digital Ledger Preview" width="95%" />
</p>

> [!TIP]
> You can also explore [`dashboard.html`](dashboard.html) directly in any modern browser for a standalone interface walkthrough.

---

## 🗺️ Roadmap & Upcoming Enhancements

- [x] Customer debit/credit tracking with balance calculations
- [x] PWA offline caching with service workers
- [x] WhatsApp payment reminder link generator
- [ ] Automated daily transaction PDF report export
- [ ] Multi-store multi-user cashier permission levels
- [ ] Cloud backup and multi-device database synchronization

---

## 👨‍💻 Author & Contact

Built and maintained by **Abdussatar** ([@abdussatarkhan](https://github.com/abdussatarkhan)).  
For technical discussions, collaboration, or queries, feel free to reach out via [LinkedIn](https://www.linkedin.com/in/abdus-satar-5150813b5/) or [GitHub](https://github.com/abdussatarkhan).

---

## 📜 License

This project is licensed under the **MIT License** — see the LICENSE file for details.

---

<div align="center">

### 👨‍💻 Maintained by [Abdussatar (@abdussatarkhan)](https://github.com/abdussatarkhan)
Part of the **[Abdussatar Software Engineering & Systems Portfolio](https://github.com/abdussatarkhan)**.

⭐ If you find this project valuable, consider dropping a star! ⭐

</div>
