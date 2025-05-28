# 🧩 Identity Reconciliation API

This is a FastAPI-based backend that solves the Bitespeed identity reconciliation problem. It intelligently links contacts by email and/or phone number into unified profiles using a primary-secondary structure.

---

## 🚀 Features

- Accepts `email` and/or `phoneNumber` as input
- Creates or links contacts intelligently
- Returns consolidated contact info with:
  - Primary contact ID
  - All related emails & phone numbers
  - List of secondary contact IDs

---

## 📦 Tech Stack

- **FastAPI** — for REST API
- **SQLAlchemy** — ORM
- **SQLite** (default) or PostgreSQL
- **Pytest** — test suite

---

## 🧪 Run Locally

### 1. Clone the repo
```bash
git clone https://github.com/Girishun/identity-recon.git
cd identity-recon
