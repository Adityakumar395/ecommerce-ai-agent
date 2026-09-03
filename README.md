# 🛒 E-Commerce AI Agent & Analytics Dashboard

[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=flat&logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-009688?style=flat&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![LangGraph](https://img.shields.io/badge/LangGraph-Agentic_Workflow-FF6F00?style=flat)](https://github.com/langchain-ai/langgraph)
[![OpenRouter](https://img.shields.io/badge/OpenRouter-AI_Models-6C5CE7?style=flat)](https://openrouter.ai/)
[![MySQL](https://img.shields.io/badge/MySQL-TiDB_Cloud-4479A1?style=flat&logo=mysql&logoColor=white)](https://www.mysql.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

An intelligent, autonomous AI-powered e-commerce analytics agent that transforms raw customer reviews and operational feedback into actionable business insights. Built with **FastAPI**, **LangGraph**, **OpenRouter**, **SQLAlchemy**, and a modern **Glassmorphic UI**.

---

## 🚀 Key Features

- 📊 **Autonomous Sentiment & Business Reporting**: Automatically extracts, groups, and summarizes customer feedback across configurable timeframes (7, 15, 30, 60, 90 days).
- 🧠 **LangGraph Agentic Architecture**: Stateful LLM graph execution with resilient multi-model routing and instant offline local fallbacks.
- 💬 **Smart "Chat with Data" (Text-to-SQL)**: Ask questions in natural English or Hinglish; the agent translates queries into safe, read-only SQL queries and returns executive answers.
- 📈 **Dynamic Visualizations**: Integrated Chart.js sentiment breakdown (Positive / Neutral / Negative) with interactive metrics.
- 📄 **Export to PDF**: One-click professional PDF export with clean print formatting.
- ☁️ **Cloud Database Ready**: Built-in support for cloud MySQL (TiDB Cloud, Aiven, AWS RDS) with auto-detecting SSL certificates.
- 🌐 **All-in-One Deployment**: FastAPI serves both high-speed API endpoints and the responsive frontend static assets.

---

## 🛠️ Tech Stack

| Layer | Technologies |
|---|---|
| **Backend** | Python 3.11, [FastAPI](https://fastapi.tiangolo.com/), [Uvicorn](https://www.uvicorn.org/) |
| **Agent / LLM** | [LangGraph](https://github.com/langchain-ai/langgraph), [LangChain](https://www.langchain.com/), OpenRouter API |
| **Database & ORM** | [SQLAlchemy](https://www.sqlalchemy.org/), PyMySQL, TiDB Cloud / MySQL |
| **Frontend** | HTML5, Vanilla CSS3 (Glassmorphism & Neon accents), JavaScript (ES6+) |
| **Libraries** | [Chart.js](https://www.chartjs.org/), [html2pdf.js](https://ekoopmans.github.io/html2pdf.js/), Font Awesome |
| **Deployment** | [Render](https://render.com) (`render.yaml`) |

---

## 📂 Project Structure

```bash
Bussiness AI Agent/
├── backend/
│   ├── .env                   # Environment variables (API keys, DB connection)
│   ├── ai_agent.py            # LangGraph state machine & sentiment engine
│   ├── database.py            # SQLAlchemy engine, session & cloud SSL config
│   ├── main.py                # FastAPI server, API routes, SQL agent & static mount
│   └── requirements.txt       # Backend dependencies
├── frontend/
│   ├── index.html             # Dashboard UI layout
│   ├── script.js              # Frontend logic, API calls, Chart.js & PDF handling
│   └── style.css              # Custom styling, dark mode & glassmorphic design
├── render.yaml                # Render deployment configuration
├── requirements.txt           # Root requirements
└── README.md                  # Project documentation
```

---

## ⚡ Getting Started

### 1. Clone the Repository
```bash
git clone https://github.com/Adityakumar395/ecommerce-ai-agent.git
cd ecommerce-ai-agent
```

### 2. Set Up Virtual Environment
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS / Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r backend/requirements.txt
```

### 4. Configure Environment Variables
Create a `.env` file inside the `backend/` directory:

```env
# OpenRouter API Key (for LLM reasoning & Text-to-SQL)
OPENROUTER_API_KEY=your_openrouter_api_key_here

# Database Connection (MySQL or TiDB Cloud)
DATABASE_URL=mysql+pymysql://<USER>:<PASSWORD>@<HOST>:<PORT>/<DATABASE>?ssl_verify_cert=true
```

> **Note**: If using TiDB Cloud or another remote MySQL provider, ensure SSL is enabled. The application automatically detects `tidbcloud.com` and configures SSL verification.

---

## 🗄️ Database Schema

The agent operates on the `reviews` table:

```sql
CREATE TABLE IF NOT EXISTS reviews (
    id INT AUTO_INCREMENT PRIMARY KEY,
    product_name VARCHAR(255) NOT NULL,
    customer_name VARCHAR(255),
    review_text TEXT NOT NULL,
    sentiment VARCHAR(50),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

---

## 🏃 Running Locally

Run the development server from the `backend/` directory:

```bash
cd backend
python -m uvicorn main:app --reload --port 8000
```

- **Dashboard UI**: [http://127.0.0.1:8000/](http://127.0.0.1:8000/)
- **Interactive Swagger API Docs**: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

---

## 🔌 API Endpoints

### 1. Generate E-Commerce Report
- **URL**: `/api/report`
- **Method**: `GET`
- **Query Params**: `days` (Default: `30`)
- **Response**:
```json
{
  "status": "success",
  "days_analyzed": 30,
  "total_reviews": 120,
  "report_html": "<div>...</div>",
  "chart_data": {
    "positive": 80,
    "negative": 25,
    "neutral": 15
  }
}
```

### 2. Chat with Database (Text-to-SQL)
- **URL**: `/api/chat`
- **Method**: `GET`
- **Query Params**: `question` (string), `days` (integer)
- **Example Queries**:
  - *"What are the top customer complaints about battery life?"*
  - *"Galaxy Smartphone ke bare me logo ne kya bola?"*
  - *"Show me sentiment count for all products"*
- **Response**:
```json
{
  "reply": "Based on 32 reviews for Galaxy Smartphone, customers praise the display but report battery drain under heavy gaming."
}
```

---

## 🚀 Deployment (Render)

This repository includes a [`render.yaml`](render.yaml) blueprint for one-click deployment:

1. Connect your GitHub repository to [Render](https://render.com).
2. Create a new **Blueprint Instance** pointing to this repo.
3. Set the environment variables in the Render dashboard:
   - `OPENROUTER_API_KEY`
   - `DATABASE_URL`
4. Deploy! The service will automatically build and start the Uvicorn web server.

---

## 🛡️ Security Features

- **Safe SQL Execution**: The agent permits only `SELECT` queries and strictly blocks destructive operations (`DROP`, `DELETE`, `UPDATE`, `ALTER`, `TRUNCATE`).
- **Resilient Fallback**: If LLM API limits are reached (HTTP 429), the system switches seamlessly to deterministic database analyzers without downtime.

---

## 📄 License

This project is licensed under the [MIT License](LICENSE).
