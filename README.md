# Digital Ledger & Store Cashbook Management System

<div align="center">

[![Daily Streak](https://img.shields.io/badge/Daily%20Streak-Active%20%F0%9F%94%A5-brightgreen?style=flat-square&logo=github)](https://github.com/abdussatarkhan)
[![Master Portfolio](https://img.shields.io/badge/Portfolio-50%2B%20Enterprise%20Projects-0e75b6?style=flat-square&logo=github)](https://github.com/abdussatarkhan/abdussatarkhan)
[![Author: Abdussatar](https://img.shields.io/badge/Author-Abdussatar-24292e?style=flat-square&logo=github)](https://github.com/abdussatarkhan)

</div>


[![CI](https://github.com/abdussatarkhan/khatabook/actions/workflows/ci.yml/badge.svg)](https://github.com/abdussatarkhan/khatabook/actions)
[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/) [![SQLite](https://img.shields.io/badge/SQLite-Local_Storage-07405E?style=for-the-badge&logo=sqlite&logoColor=white)](https://www.sqlite.org/) [![Accounting](https://img.shields.io/badge/FinTech-Ledger_Engine-2E7D32?style=for-the-badge)](https://en.wikipedia.org/wiki/Ledger)
[![Author](https://img.shields.io/badge/Author-Abdussatar-E50914?style=for-the-badge&logo=github&logoColor=white)](https://github.com/abdussatarkhan)

> **A digital accounting ledger and merchant credit manager designed for small business shopkeepers to track customer debit/credit transactions (Udhar), generate automated WhatsApp payment reminders, and reconcile daily cash flows.**

---

## 🏛️ System Architecture

```mermaid
graph TD
    MerchantUI[Merchant Dashboard & Ledger UI] --> Logic[Accounting & Transaction Core Engine]
    Logic --> LedgerDB[(Encrypted Local SQLite Database)]
    Logic --> Reminder[Automated Customer SMS / WhatsApp Notification Engine]
    Logic --> Reports[Daily P&L & Cash Flow PDF Exporter]
```

---

## 🌟 Key Features & Capabilities

- **Production-Grade Implementation**: Built with modular design patterns, type safety, and clean separation of concerns.
- **Robust Ledger & Data Persistence**: ACID-compliant transactions and optimized queries.
- **Comprehensive Tech Stack**: `Python` `SQLite` `FinTech` `Ledger Accounting` `Automation`.

---

## 🚀 Quickstart & Setup

### 1. Clone the Repository
```bash
git clone https://github.com/abdussatarkhan/khatabook.git
cd khatabook
```

---

## 🗺️ Roadmap & Upcoming Features

- [x] Digital customer debit/credit ledger (Udhar tracking)
- [x] Local SQLite encrypted database persistence
- [ ] Automated WhatsApp / SMS payment reminder integration
- [ ] Daily cash flow summary PDF report generator
- [ ] Multi-device cloud sync and backup

---

## 👨‍💻 Author & Profile

Built and maintained by **Abdussatar** ([@abdussatarkhan](https://github.com/abdussatarkhan)).  
For collaboration or queries, feel free to reach out via [LinkedIn](https://www.linkedin.com/in/abdus-satar-5150813b5/) or [GitHub](https://github.com/abdussatarkhan).

---

## 📜 License

This project is licensed under the **MIT License** — see the LICENSE file for details.


---

<div align="center">

### 👨‍💻 Maintained by [Abdussatar (@abdussatarkhan)](https://github.com/abdussatarkhan)
Part of the **[Master Enterprise Data Analytics & AI Portfolio](https://github.com/abdussatarkhan/abdussatarkhan)**.

⭐ If you find this repository valuable, consider dropping a star! ⭐

</div>
