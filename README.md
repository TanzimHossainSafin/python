# 🐍 Python Projects Collection

A collection of advanced Python projects demonstrating algorithmic trading and AI-powered chatbot systems with web scraping capabilities.

[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![GitHub](https://img.shields.io/badge/GitHub-TanzimHossainSafin-181717.svg?logo=github)](https://github.com/TanzimHossainSafin)

---

## 📑 Table of Contents

- [Overview](#overview)
- [Projects](#projects)
  - [Task 1: Algorithmic Trading System](#task-1-algorithmic-trading-system)
  - [Task 2: Samsung Phone Advisor](#task-2-samsung-phone-advisor)
- [Repository Structure](#repository-structure)
- [Installation](#installation)
- [Usage](#usage)
- [Technologies Used](#technologies-used)
- [Contributing](#contributing)
- [License](#license)
- [Author](#author)

---

## 🔍 Overview

This repository contains two distinct Python projects showcasing different domains of software development:

1. **Algorithmic Trading System** - A Golden Cross/Death Cross trading strategy implementation using historical stock data
2. **Samsung Phone Advisor** - An AI-powered chatbot using RAG (Retrieval-Augmented Generation) and Multi-Agent architecture with web scraping

---

## 🚀 Projects

### Task 1: Algorithmic Trading System

<img src="https://img.shields.io/badge/Finance-Trading-brightgreen" alt="Finance Trading">

A sophisticated algorithmic trading system that implements the **Golden Cross / Death Cross** strategy for automated stock trading decisions.

#### 📊 Strategy Overview

- **Golden Cross** (🟢 BUY Signal): Occurs when the 50-day Moving Average (MA50) crosses **above** the 200-day Moving Average (MA200)
- **Death Cross** (🔴 SELL Signal): Occurs when the 50-day Moving Average (MA50) crosses **below** the 200-day Moving Average (MA200)
- **Budget**: $5,000 (configurable)

#### ✨ Key Features

| Feature | Description |
|---------|-------------|
| **Data Acquisition** | Downloads historical OHLCV data using `yfinance` |
| **Data Cleaning** | Removes duplicates and handles missing values |
| **Technical Analysis** | Computes 50-day and 200-day simple moving averages |
| **Signal Detection** | Identifies Golden Cross and Death Cross patterns |
| **Trade Execution** | Automated buy/sell decisions with position management |
| **Performance Summary** | Detailed trade logs and P&L calculations |

#### 🎯 How It Works

```
1. Data Acquisition
   ↓
2. Data Cleanup (Remove duplicates, fill NaN)
   ↓
3. Calculate Moving Averages (MA50, MA200)
   ↓
4. Detect Crossover Signals
   ↓
5. Execute Trades (BUY on Golden Cross, SELL on Death Cross)
   ↓
6. Generate Summary Report
```

#### 💻 Usage Example

```python
from task1 import AlgorithmicTrader

# Initialize the trader
trader = AlgorithmicTrader(
    symbol="AAPL",           # Stock ticker symbol
    from_date="2018-01-01",  # Start date
    to_date="2023-12-31",    # End date
    budget=5000              # Initial investment
)

# Run the trading strategy
profit = trader.run()
```

#### 📈 Sample Output

```
═══════════════════════════════════════════════════════════════════════════
  Algorithmic Trading Strategy  │  AAPL
  Period : 2018-01-01  →  2023-12-31
  Budget : $5,000.00
═══════════════════════════════════════════════════════════════════════════

2018-04-02 │ BUY        │ Price: $  167.78 │ Shares:    29 │ Cost:    $ 4,865.62
2018-06-26 │ SELL       │ Price: $  182.17 │ Shares:    29 │ Revenue: $ 5,282.93 │ Profit: $   +417.31
2019-05-07 │ BUY        │ Price: $  202.86 │ Shares:    24 │ Cost:    $ 4,868.64
2019-08-23 │ SELL       │ Price: $  202.75 │ Shares:    24 │ Revenue: $ 4,866.00 │ Profit: $     -2.64

═══════════════════════════════════════════════════════════════════════════
  SUMMARY
───────────────────────────────────────────────────────────────────────────
  Completed Trades : 5
  Total P&L        : $+1,234.56
  Final Balance    : $6,234.56  (started with $5,000.00)
══════��══════════════════���═════════════════════════════════════════════════
```

#### 🔧 Dependencies

```
yfinance>=0.2.0
pandas>=1.5.0
```

#### 📁 File

- **`task1.py`** - Main trading system implementation (185 lines)

---

### Task 2: Samsung Phone Advisor

<img src="https://img.shields.io/badge/AI-RAG%20%7C%20Multi--Agent-blueviolet" alt="AI RAG Multi-Agent">

An intelligent chatbot system that answers natural-language questions about Samsung smartphones using **RAG (Retrieval-Augmented Generation)** and a **Multi-Agent architecture** powered by Claude AI (Anthropic).

#### 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    User Query (FastAPI)                     │
└───────────────────────┬─────────────────────────────────────┘
                        │
                        ↓
┌─────────────────────────────────────────────────────────────┐
│              Step 1: RAG Module (rag.py)                    │
│  • Extract model names from query                           │
│  • Retrieve phone specs from PostgreSQL                     │
│  • Build context for LLM                                    │
└───────────────────────┬─────────────────────────────────────┘
                        │
                        ↓
┌─────────────────────────────────────────────────────────────┐
│         Step 2: Multi-Agent System (agents.py)              │
│                                                              │
│  ┌─────────────────────────────────────────────────┐        │
│  │  Agent 1: Data Extractor (Tool-Use)             │        │
│  │  • search_phones_by_name()                      │        │
│  │  • get_all_phones()                             │        │
│  │  • Returns structured JSON data                 │        │
│  └──────────────────┬──────────────────────────────┘        │
│                     │                                        │
│                     ↓                                        │
│  ┌───────────────────────────────��─────────────────┐        │
│  │  Agent 2: Review Generator                      │        │
│  │  • Receives structured data                     │        │
│  │  • Generates natural language response          │        │
│  │  • Handles specs, comparisons, recommendations  │        │
│  └─────────────────────────────────────────────────┘        │
└───────────────────────┬─────────────────────────────────────┘
                        │
                        ↓
┌─────────────────────────────────────────────────────────────┐
│                 Natural Language Answer                     │
└─────────────────────────────────────────────────────────────┘
```

#### ✨ Key Features

- **🔍 Web Scraping**: Automatically scrapes Samsung phone specifications from GSMArena
- **💾 PostgreSQL Database**: Stores phone data with connection pooling for efficiency
- **🤖 AI-Powered Responses**: Uses Claude (Anthropic) with tool-calling capabilities
- **🔗 RAG Pipeline**: Retrieves relevant specs before generating answers
- **🎯 Multi-Agent System**: 
  - **Agent 1**: Extracts structured data using tool calls
  - **Agent 2**: Generates polished natural language reviews
- **🚀 FastAPI Backend**: RESTful API with automatic documentation
- **📊 Smart Query Handling**: Supports specs lookup, comparisons, and recommendations

#### 🗂️ Database Schema

```sql
CREATE TABLE samsung_phones (
    id           SERIAL PRIMARY KEY,
    model_name   VARCHAR(255) UNIQUE NOT NULL,
    release_date VARCHAR(200),
    display      VARCHAR(500),
    battery      VARCHAR(200),
    camera       TEXT,
    ram          VARCHAR(200),
    storage      VARCHAR(200),
    price        VARCHAR(200),
    full_specs   TEXT,
    created_at   TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### 🛠️ Setup Instructions

##### 1️⃣ Install Dependencies

```bash
cd task2
pip install -r requirements.txt
```

##### 2️⃣ Configure Environment

Create a `.env` file from the example:

```bash
cp .env.example .env
```

Edit `.env` with your credentials:

```env
# PostgreSQL connection
DB_HOST=localhost
DB_PORT=5432
DB_NAME=samsung_advisor
DB_USER=postgres
DB_PASSWORD=your_postgres_password

# Anthropic API key (get from https://console.anthropic.com)
ANTHROPIC_API_KEY=sk-ant-xxxxxxxxxxxxxxxxxxxxxxxxxxxxx

# Number of phones to scrape (default: 25)
SCRAPE_TARGET=25
```

##### 3️⃣ Set Up PostgreSQL Database

```bash
# Install PostgreSQL (Ubuntu/Debian)
sudo apt-get install postgresql postgresql-contrib

# Create database
sudo -u postgres psql
CREATE DATABASE samsung_advisor;
\q
```

##### 4️⃣ Scrape Phone Data

```bash
python scraper.py
```

**Output:**
```
2026-02-26 10:30:15  INFO      __main__  Listing page 1: https://www.gsmarena.com/samsung-phones-9.php
2026-02-26 10:30:16  INFO      __main__  ✅ Samsung Galaxy S23 Ultra
2026-02-26 10:30:17  INFO      __main__  ✅ Samsung Galaxy Z Fold 5
...
2026-02-26 10:32:45  INFO      __main__  Scraped 25 phones successfully!
```

##### 5️⃣ Start the FastAPI Server

```bash
uvicorn main:app --reload
```

**Server will start at:** `http://localhost:8000`

---

#### 🌐 API Endpoints

##### 1. **POST /ask** - Ask a Question

**Request:**
```bash
curl -X POST "http://localhost:8000/ask" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What are the specs of Samsung Galaxy S23 Ultra?"
  }'
```

**Response:**
```json
{
  "answer": "The Samsung Galaxy S23 Ultra features a stunning 6.8-inch Dynamic AMOLED 2X display with 120Hz refresh rate. It's powered by a 5000mAh battery supporting 45W fast charging. The camera system includes a 200MP main sensor, 12MP ultra-wide, and dual telephoto lenses (10MP 3x and 10MP 10x). It comes with 8/12GB RAM and storage options up to 1TB. Launched in February 2023, it's priced starting at $1,199."
}
```

**More Example Questions:**
- `"Compare Galaxy S23 Ultra and S22 Ultra for photography"`
- `"Which Samsung phone has the best battery under $1000?"`
- `"What's the difference between Galaxy Z Fold 5 and Z Flip 5?"`
- `"Recommend a Samsung phone for gaming"`

##### 2. **GET /phones** - List All Phones

```bash
curl "http://localhost:8000/phones"
```

##### 3. **GET /health** - Health Check

```bash
curl "http://localhost:8000/health"
```

##### 4. **GET /docs** - Interactive API Documentation

Visit: `http://localhost:8000/docs` (Swagger UI)

---

#### 📂 Module Descriptions

| File | Description | Lines |
|------|-------------|-------|
| **`main.py`** | FastAPI application with endpoints for querying phone information | 116 |
| **`agents.py`** | Multi-agent system using Claude AI with tool-calling for data extraction and response generation | ~200 |
| **`rag.py`** | RAG module for retrieving relevant phone specs from PostgreSQL | 83 |
| **`database.py`** | PostgreSQL connection pooling, schema initialization, and CRUD operations | 110 |
| **`scraper.py`** | Web scraper for GSMArena to extract Samsung phone specifications | ~180 |
| **`config.py`** | Configuration management for environment variables | 25 |
| **`requirements.txt`** | Python dependencies | 7 |
| **`.env.example`** | Environment variable template | 14 |

---

#### 🔧 Dependencies

```
fastapi==0.115.0
uvicorn[standard]==0.30.6
psycopg2-binary==2.9.9
requests==2.32.3
beautifulsoup4==4.12.3
anthropic==0.40.0
python-dotenv==1.0.1
```

---

#### 🎯 How Each Module Works

##### `scraper.py` - Web Scraping Module
```python
scraper = GSMArenaPhoneScraper(target_count=25)
phone_links = scraper.get_phone_links()  # Step 1: Get listing URLs
for link in phone_links:
    phone_data = scraper.scrape_phone(link)  # Step 2: Extract specs
    upsert_phone(phone_data)  # Step 3: Save to PostgreSQL
```

##### `rag.py` - Retrieval Module
```python
from rag import rag_retrieve

phones, context = rag_retrieve("Galaxy S23 Ultra battery")
# Returns: List of phone dicts + formatted context string
```

##### `agents.py` - Multi-Agent System
```python
from agents import run_multi_agent

answer = run_multi_agent("Compare S23 and S22 for gaming")
# Agent 1: Calls search_phones_by_name("S23"), search_phones_by_name("S22")
# Agent 2: Generates comparison review from structured data
```

##### `database.py` - Database Operations
```python
from database import initialize_db, search_phones_by_name, get_all_phones

initialize_db()  # Creates table if not exists
phones = search_phones_by_name("Galaxy S23")  # Search by model
all_phones = get_all_phones()  # Get all records
```

---

## 📁 Repository Structure

```
python/
├── .gitignore                  # Git ignore file
├── README.md                   # This file
│
├── task1.py                    # Algorithmic Trading System (185 lines)
│
└── task2/                      # Samsung Phone Advisor
    ├── agents.py               # Multi-agent system with Claude AI
    ├── config.py               # Configuration management
    ├── database.py             # PostgreSQL operations
    ├── main.py                 # FastAPI application
    ├── rag.py                  # Retrieval-Augmented Generation module
    ├── scraper.py              # GSMArena web scraper
    ├── requirements.txt        # Python dependencies
    └── .env.example            # Environment variables template
```

---

## 📦 Installation

### Prerequisites

- Python 3.9 or higher
- PostgreSQL 12+ (for Task 2)
- pip package manager

### Clone the Repository

```bash
git clone https://github.com/TanzimHossainSafin/python.git
cd python
```

### Install Dependencies

#### For Task 1:
```bash
pip install yfinance pandas
```

#### For Task 2:
```bash
cd task2
pip install -r requirements.txt
```

---

## 🎮 Usage

### Task 1: Algorithmic Trading

```bash
python task1.py
```

**Customize the strategy:**
```python
trader = AlgorithmicTrader(
    symbol="TSLA",           # Change stock ticker
    from_date="2020-01-01",  # Adjust date range
    to_date="2024-12-31",
    budget=10000             # Modify budget
)
trader.run()
```

### Task 2: Samsung Phone Advisor

#### Step 1: Scrape Data
```bash
cd task2
python scraper.py
```

#### Step 2: Start Server
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

#### Step 3: Query the API

**Using cURL:**
```bash
curl -X POST "http://localhost:8000/ask" \
  -H "Content-Type: application/json" \
  -d '{"question": "Best Samsung phone for photography?"}'
```

**Using Python:**
```python
import requests

response = requests.post(
    "http://localhost:8000/ask",
    json={"question": "What are the specs of Galaxy Z Fold 5?"}
)
print(response.json()["answer"])
```

**Using JavaScript (fetch):**
```javascript
fetch('http://localhost:8000/ask', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ question: 'Compare S23 Ultra vs S24 Ultra' })
})
.then(res => res.json())
.then(data => console.log(data.answer));
```

---

## 🛠️ Technologies Used

### Task 1: Algorithmic Trading
- **Python** - Core programming language
- **yfinance** - Historical stock data retrieval
- **Pandas** - Data manipulation and analysis
- **NumPy** - Numerical computations

### Task 2: Samsung Phone Advisor
- **Python** - Core programming language
- **FastAPI** - Modern web framework for APIs
- **PostgreSQL** - Relational database
- **psycopg2** - PostgreSQL adapter
- **Anthropic Claude** - AI language model
- **BeautifulSoup4** - Web scraping
- **Requests** - HTTP library
- **python-dotenv** - Environment variable management

---

## 🤝 Contributing

Contributions are welcome! Here's how you can help:

1. **Fork the repository**
2. **Create a feature branch**
   ```bash
   git checkout -b feature/amazing-feature
   ```
3. **Commit your changes**
   ```bash
   git commit -m 'Add some amazing feature'
   ```
4. **Push to the branch**
   ```bash
   git push origin feature/amazing-feature
   ```
5. **Open a Pull Request**

### Contribution Guidelines

- Follow PEP 8 style guide for Python code
- Add docstrings to all functions and classes
- Write unit tests for new features
- Update documentation as needed

---

## 📄 License

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.

```
MIT License

Copyright (c) 2026 Tanzim Hossain Safin

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software...
```

---

## 👤 Author

**Tanzim Hossain Safin**

- 🐙 GitHub: [@TanzimHossainSafin](https://github.com/TanzimHossainSafin)
- 📧 Email: [Contact via GitHub](https://github.com/TanzimHossainSafin)
- 🌐 Portfolio: [TanzimHossainSafin](https://github.com/TanzimHossainSafin)

---

## 🙏 Acknowledgments

- **yfinance** - For providing free stock market data
- **GSMArena** - For comprehensive phone specifications
- **Anthropic** - For Claude AI API
- **FastAPI** - For the excellent web framework
- **PostgreSQL** - For reliable database management

---

## 📊 Project Stats

![GitHub repo size](https://img.shields.io/github/repo-size/TanzimHossainSafin/python)
![GitHub last commit](https://img.shields.io/github/last-commit/TanzimHossainSafin/python)
![GitHub stars](https://img.shields.io/github/stars/TanzimHossainSafin/python?style=social)

---

## 🔮 Future Enhancements

### Task 1:
- [ ] Add more trading strategies (RSI, MACD, Bollinger Bands)
- [ ] Implement backtesting visualization
- [ ] Add risk management features
- [ ] Support for multiple assets simultaneously
- [ ] Real-time trading capabilities

### Task 2:
- [ ] Add more phone brands (Apple, Google, OnePlus)
- [ ] Implement vector embeddings for better search
- [ ] Add user authentication and history
- [ ] Create a frontend web interface
- [ ] Support image-based queries
- [ ] Add price tracking and alerts

---

## 📚 Learn More

### Algorithmic Trading Resources:
- [Investopedia - Moving Averages](https://www.investopedia.com/terms/m/movingaverage.asp)
- [Golden Cross vs Death Cross](https://www.investopedia.com/terms/g/goldencross.asp)

### RAG & Multi-Agent Systems:
- [Anthropic Documentation](https://docs.anthropic.com/)
- [RAG Explained](https://www.anthropic.com/research/retrieval-augmented-generation)
- [Multi-Agent Systems](https://arxiv.org/abs/2308.08155)

---

<div align="center">

**⭐ Star this repository if you find it helpful!**

Made with ❤️ by [Tanzim Hossain Safin](https://github.com/TanzimHossainSafin)

</div>
