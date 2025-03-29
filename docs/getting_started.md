# Getting Started with B-vista

Welcome to **B-vista** — an enterprise-grade, full-stack Exploratory Data Analysis (EDA) tool for working with `pandas` DataFrames using an intuitive, visual, real-time interface.

This guide walks you through setting up the project locally, launching both the backend and frontend, and using B-vista inside a notebook or browser.

---

## 🚀 Prerequisites

Make sure you have the following installed:

- **Python**: `>=3.7`
- **Node.js**: `^18.x`
- **npm**: `^9.x`

You can verify your versions with:

```bash
python --version
node -v
npm -v
```

---

## 📦 Clone the Repository

```bash
git clone https://github.com/Baci-Ak/b-vista.git
cd b-vista
```

---

## 🧠 Backend Setup (Flask + WebSockets)

1. **Create virtual environment (optional but recommended):**

```bash
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

2. **Install Python dependencies:**

```bash
pip install -r requirements.txt
```

3. **Run the Flask server:**

```bash
python backend/app.py
```

- Runs on: `http://localhost:5050`
- WebSocket support is included via `Flask-SocketIO`

> 📸 **[Placeholder: Screenshot of backend running in terminal]**

---

## 🖼️ Frontend Setup (React + Vite)

1. **Navigate to the frontend directory:**

```bash
cd frontend
```

2. **Install npm dependencies:**

```bash
npm install
```

3. **Start the React development server:**

```bash
npm start
```

- Runs on: `http://localhost:3000`
- Communicates with Flask backend on port `5050`

> 📸 **[Placeholder: Screenshot of frontend UI loaded]**

---

## 🧪 Launch from a Jupyter Notebook

You can use B-vista inside your notebooks using:

```python
import pandas as pd
import bvista

df = pd.read_csv("your_data.csv")
bvista.show(df)
```

- Automatically starts the backend
- Opens the UI in your browser or notebook iframe
- Requires `bvista` module (see: [setup.py](../../setup.py))

> 📸 **[Placeholder: Screenshot of notebook integration]**

---

## 🐞 Common Troubleshooting

### ⚠️ Frontend build issues (Vite)
```bash
rm -rf node_modules package-lock.json
npm install
```

Make sure Node.js version is v18+

### ⚠️ Flask server not reachable
- Make sure nothing else is using port `5050`
- Check for firewall or CORS issues (see `backend/config.py`)

### ⚠️ WebSocket not connecting
- Ensure backend and frontend are both running
- Reload page after backend starts

---

## ✅ Success!

Once everything is running:

- Visit `http://localhost:3000`
- Upload a CSV or launch from a notebook
- Explore data visually and in real time

> 🎥 **[Placeholder: GIF showing loading a CSV and switching views]**

---

## 🔗 What Next?

- Read the [Features](../features.md)
- Dive into [Jupyter Integration](usage/jupyter_notebook.md)
- Explore API and WebSocket Events in [Usage](usage/web_interface.md)
- Start contributing: [Development Guide](../development/architecture.md)

---

> Need help? Open an issue or start a discussion on the [GitHub repo](https://github.com/Baci-Ak/b-vista)

