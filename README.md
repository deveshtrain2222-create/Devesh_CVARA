## 📊 Crypto Volatility and Risk Analyzer (CVARA)

A database-driven analytical dashboard to analyze cryptocurrency price volatility, financial risk metrics, and risk classification using historical market data.

---

## 📌 Project Overview

The Crypto Volatility and Risk Analyzer (CVARA) is a Python-based project that evaluates the risk profile of cryptocurrencies using historical price data stored in a relational database.

Instead of relying on flat files, the project uses a structured database (SQLite / MySQL) to store price history and computed risk metrics.
The system computes important financial indicators such as Volatility, Sharpe Ratio, Beta, and Value at Risk (VaR) and visualizes them through interactive dashboards.

The project follows a milestone-based architecture, covering data ingestion, database storage, analytics, visualization, and reporting.

---

## 🎯 Objectives

    Fetch historical cryptocurrency price data from public APIs
    
    Store market data in a database for structured access
    
    Calculate daily returns and volatility
    
    Compute risk metrics (Sharpe Ratio, Beta, VaR)
    
    Classify assets into High / Medium / Low risk categories
    
    Present insights using interactive dashboards
    
    Generate downloadable CSV and PDF risk reports

---

## 🧩 Project Milestones (Database-Oriented)

### 🔹 Milestone 1: Data Ingestion & Storage

    Cryptocurrency price data fetched using CoinGecko API
    
    Data stored in a relational database (SQLite / MySQL)
    
    Separate tables used for coins and historical prices

### 🔹 Milestone 2: Data Processing

    Price data loaded directly from the database
    
    Daily returns calculated using stored prices
    
    Volatility and normalization applied using Pandas & NumPy

###  🔹 Milestone 3: Visualization Dashboard

    Interactive dashboards built using Dash & Plotly
    
    Price trend charts from database records
    
    Volatility trend charts
    
    Risk–Return scatter plots
    
    KPI indicators

### 🔹 Milestone 4: Risk Classification & Reporting

    Risk classification based on volatility thresholds
    
    High / Medium / Low risk grouping
    
    Risk distribution pie chart
    
    Risk metrics stored back into the database
    
    PDF and CSV reports generated from database data

---    

##  🛠️ Tech Stack

    Programming Language: Python
    
    Backend Framework: Flask
    
    Dashboard Framework: Dash (Plotly)
    
    Database: SQLite / MySQL
    
    Data Analysis: Pandas, NumPy
    
    Visualization: Plotly
    
    Reporting: ReportLab
    
    Version Control: Git & GitHub

---    

## 🗄️ Database Design

### Main Tables Used:
    
    Cryptocurrency – stores coin metadata
    
    PriceData – stores historical price records
    
    RiskMetrics – stores calculated risk values
    
    User / Portfolio (optional) – for extensibility

### The database ensures:

    Structured data storage
    
    Faster querying
    
    No redundancy
    
    Better scalability compared to CSV files

---    

## 📂 Project Structure

### crypto-volatility-risk-analyzer/
    
    │
    ├── app.py                  # Flask main server
    ├── db.py                   # Database connection & schema
    ├── mil3_dash.py             # Milestone 3 – Visualization Dashboard
    ├── mil4_dash.py             # Milestone 4 – Risk Classification & Reporting
    │
    ├── database/
    │   └── cvara.db             # SQLite database
    │
    ├── templates/               # HTML templates
    ├── static/                  # CSS, images
    │
    ├── OUTPUTS/                 # Dashboard screenshots & reports
    ├── requirements.txt
    ├── .gitignore
    └── README.md

---

## 🚀 How to Run the Project

### 1️⃣ Clone the Repository

``git clone https://github.com/deveshtrain2222-create/Devesh_CVARA.git``

``cd Devesh_CVARA``

### 2️⃣ Install Dependencies

``pip install -r requirements.txt``

### 3️⃣ Run the Application

``python app.py``

✔ On startup, the database tables are created automatically

✔ Historical data is fetched and stored in the database

### 4️⃣ Open in Browser

``http://127.0.0.1:5000``

---

## 📊 Key Features

    ⚫ Database-driven data storage
    ⚫ Multi-cryptocurrency selection
    ⚫ Interactive price & volatility charts
    ⚫ Risk–Return analysis
    ⚫ Automated risk classification
    ⚫ Risk distribution visualization
    ⚫ CSV & PDF report generation
    ⚫ Modern glassmorphism UI

---    

## 📈 Diagrams
### 1️⃣ System Workflow Diagram

(API → Database → Processing → Dashboard)

<img width="1153" height="322" alt="image" src="https://github.com/user-attachments/assets/5785e257-27ef-40fe-b0e5-de53bc7f70d9" />


### 2️⃣ Architecture Diagram

(Flask + Database + Dash)

<img width="453" height="319" alt="image" src="https://github.com/user-attachments/assets/48ab8146-ab56-4feb-88d0-81b7de39d7eb" />


### 3️⃣ Database Schema Diagram

(Cryptocurrency, PriceData, RiskMetrics relationships)

<img width="459" height="320" alt="image" src="https://github.com/user-attachments/assets/dc61a490-0fbf-406c-8693-00d9378316ce" />


---

## 📄 Reports

    ⚫ CSV Report – Exported directly from database
    ⚫ PDF Report – Summarized risk analysis for academic submission

---    

##  ✅ Conclusion

###  This project demonstrates a complete data analytics pipeline using a database-centric approach:

    Reliable data storage
    
    Financial risk analysis
    
    Interactive visualization
    
    Professional reporting

### It showcases practical application of databases, financial analytics, and data visualization in the cryptocurrency domain.

---

## 👨‍💻 Author
## Devesh Gautam
`` B.Tech – Computer Science & Engineering``
