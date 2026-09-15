# 🛡️ FRAUDGUARD AI — AI-Powered Transaction Security Platform

**FRAUDGUARD AI** is a real-time, explainable transaction security platform designed to protect financial transactions against fraudulent activity and pattern anomalies.

Instead of binary "fraud / non-fraud" predictions, FRAUDGUARD AI calculates a nuanced **Risk Score (0–100%)**, classifies payments into clear safety levels (🟢 **SAFE**, 🟡 **CHECK**, 🔴 **HIGH RISK**), and provides dynamic, plain-language explanations detailing **WHY** a payment was flagged.

---

## 🌟 Key Features

1. **Dual ML Engine Architecture**:
   - **Supervised Classifier**: `RandomForestClassifier` with `class_weight="balanced"` trained on 15,000 synthetic transaction records across multiple fraud typologies.
   - **Unsupervised Anomaly Detector**: `IsolationForest` to detect novel zero-day behavioral deviations.
2. **Centralized Risk Engine**: Fuses ML probabilities, IsolationForest outlier scores, time-of-day flags, location jumps, device novelty, and velocity spikes (transactions in last 10 min).
3. **Plain-Language Explainability**: Translates complex feature contribution vectors into non-technical, human-understandable safety reasons (e.g. *"Payment amount is 5x higher than usual average"*, *"New device used"*).
4. **Interactive Payment Checker**: Real-time payment verification with live risk meters, instant decisioning, and demo presets.
5. **AI Investigation Assistant**: Deterministic investigation chatbot grounded strictly in empirical transaction data (works 100% offline without external LLM keys).
6. **Decision & Action Audit**: Allows analysts to **Allow**, **Review**, or **Block** payments, saving decision audit trails in SQLite database.
7. **Automated PDF Reports**: Generates downloadable ReportLab PDF security and fraud audit reports.
8. **Responsive Banking Design**: Clean, accessible visual design with dark/light mode toggle, mobile drawer navigation, and accessible indicators.

---

## 📐 Technology Stack

- **Frontend**: HTML5, CSS3, JavaScript (ES6+), Bootstrap 5 / Custom CSS System, Chart.js, FontAwesome 6
- **Backend**: Python 3.10+, Flask, Flask-CORS, Flask-SQLAlchemy
- **Machine Learning**: `scikit-learn`, `pandas`, `numpy`, `joblib`
- **Report Generation**: `reportlab`
- **Database**: SQLite (SQLAlchemy ORM)
- **Testing**: `pytest`

---

## 📁 Project Structure

```
FRAUDGUARD-AI/
│
├── app.py                      # Flask Application Server & Seeder
├── config.py                   # Global configuration & file paths
├── generate_data.py            # Generates 15,000 realistic transaction records
├── requirements.txt            # Dependencies manifest
├── .gitignore                  # Git ignore rules
├── .env.example                # Sample environment variables
│
├── data/
│   ├── transactions.csv        # 15,000 records dataset
│   └── sample_transactions.csv # 100 records sample
│
├── models/
│   ├── fraud_model.pkl         # Trained Random Forest model
│   ├── anomaly_model.pkl       # Trained Isolation Forest model
│   ├── scaler.pkl              # Fitted StandardScaler
│   └── model_metadata.json     # Metrics (Precision, Recall, F1, ROC-AUC, PR-AUC)
│
├── database/
│   ├── schema.py               # SQLAlchemy ORM Models (Transaction, FraudAlert, Action, Setting)
│   └── fraudguard.db           # SQLite Database File
│
├── ml/
│   ├── __init__.py
│   ├── preprocessing.py        # Feature extraction & scaling pipeline
│   ├── train_model.py          # Unified model training & evaluation script
│   ├── fraud_detector.py       # Supervised inference wrapper
│   ├── anomaly_detector.py     # Unsupervised anomaly inference wrapper
│   └── explainability.py       # Rule & contribution explanation engine
│
├── services/
│   ├── risk_engine.py          # Risk score calculation & signal fusion
│   ├── transaction_service.py  # Database CRUD & analytics aggregation
│   └── report_service.py       # ReportLab PDF report builder
│
├── routes/
│   ├── __init__.py
│   ├── dashboard.py            # Stats & recent payments API
│   ├── transactions.py         # Search, filter, pagination API
│   ├── reports.py              # Report summary & PDF download API
│   ├── settings.py             # App preferences API
│   └── checker.py              # Safety check, demo presets, & AI assistant API
│
├── templates/
│   ├── layout.html             # Base template with fixed responsive sidebar
│   ├── index.html              # Home Dashboard ("Is Your Money Safe?")
│   ├── transactions.html       # My Transactions Management Table
│   ├── suspicious.html         # Suspicious Payments Alert Center
│   ├── safety_check.html       # Dedicated Payment Safety Checker
│   ├── ai_check.html           # AI Workflow & Technical Judge Accordion
│   ├── activity.html           # Chart.js Analytics & Risk Trends
│   ├── reports.html            # PDF Report Download & Preview
│   └── settings.html           # System Settings & Theme Toggle
│
├── static/
│   ├── css/style.css           # Clean Banking Security Design System
│   └── js/
│       ├── app.js              # Theme toggle, toast alerts, modal drawer
│       ├── dashboard.js        # Home stats, recent table, quick checker
│       ├── transactions.js     # Table filter, search, sort, pagination
│       ├── checker.js          # Safety check form & AI assistant
│       └── charts.js           # Chart.js visualizations
│
└── tests/
    ├── test_model.py           # Feature engineering & ML inference tests
    └── test_risk_engine.py     # Risk engine score calculation tests
```

---

## ⚡ Quick Start & Setup Instructions

### 1. Environment Setup

```bash
# Clone or navigate to the repository directory
cd FRAUDGUARD-AI

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows PowerShell / CMD:
venv\Scripts\activate
# On macOS / Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Generate Synthetic Dataset (15,000 Transactions)

```bash
python generate_data.py
```

### 3. Train Machine Learning Models

```bash
python ml/train_model.py
```

*Output displays Precision, Recall, F1, ROC-AUC, PR-AUC, and Confusion Matrix metrics.*

### 4. Run Application Server

```bash
python app.py
```

Open your web browser and visit: **`http://127.0.0.1:5000`**

---

## 🧪 Running Automated Tests

Run the comprehensive unit and integration test suite:

```bash
pytest tests/
```

---

## 📊 Hackathon Demo Scenario Instructions

To demonstrate the full power of FRAUDGUARD AI in 3 minutes:

1. **Dashboard Overview**: Open `http://127.0.0.1:5000`. Observe the summary cards dynamically loaded from the database (`15,000 Total Payments`).
2. **Normal Payment Check**: Under **Check a Payment**, click the **🟢 Safe** demo preset button and click **Check Now**. Watch the system return **🟢 SAFE PAYMENT (Risk: ~8%)**.
3. **Suspicious Activity Check**: Click the **🟡 Suspicious** demo preset button and click **Check Now**. Note the **🟡 CHECK THIS PAYMENT** banner and dynamic reasons (*"Multiple payments initiated in last 10 minutes"*).
4. **High Risk Fraud Check**: Click the **🔴 High Risk** demo preset button and click **Check Now**. Observe **🔴 HIGH RISK (Risk: ~87%)** with reasons (*"Unrecognized device"*, *"Unusual geo-location"*).
5. **Take Manual Action**: Click **Block Payment**. Note that the decision updates the transaction status to `BLOCKED` in the database.
6. **Suspicious Payments View**: Navigate to **🚨 Suspicious Payments** in the sidebar to review flagged transactions.
7. **AI Check Page & Judge Section**: Open **🤖 AI Check** to see the 4 simple user steps. Expand the **Technical Architecture Details** accordion to view empirical model evaluation metrics (**PR-AUC**, **ROC-AUC**, feature importances).
8. **Download PDF Report**: Navigate to **📄 Reports** and click **Download PDF Report** to generate the official ReportLab PDF document.

---

## 🔗 REST API Endpoints Summary

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/api/stats` | Dashboard statistics (Total, Safe, Need Checking, Fraud Alerts, Blocked) |
| `GET` | `/api/recent-transactions` | Top 5 recent transactions |
| `GET` | `/api/transactions` | Paginated, searchable, filterable transaction list |
| `GET` | `/api/transactions/<id>` | Transaction detail by ID |
| `POST` | `/api/check` | Real-time ML payment risk evaluation & DB save |
| `POST` | `/api/transactions/<id>/action` | Update decision status (`ALLOW`, `REVIEW`, `BLOCK`) |
| `GET` | `/api/suspicious` | List of suspicious/anomalous transactions |
| `GET` | `/api/activity` | Chart analytics datasets |
| `GET` | `/api/reports` | Report summary metrics |
| `GET` | `/api/reports/download` | Downloads ReportLab PDF security report |
| `GET/PUT` | `/api/settings` | Retrieve or update system settings |
| `POST` | `/api/ai/investigate` | Grounded AI Investigation Assistant |
