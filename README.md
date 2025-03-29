

---

<!-- B-vista README.md -->

# 📊 B-vista

> **Visual, Scalable, and Real-Time Exploratory Data Analysis — Built for modern notebooks and the browser.**

---

![build](https://img.shields.io/badge/build-passing-brightgreen)  
![python](https://img.shields.io/badge/python-3.7%2B-blue)  
![license](https://img.shields.io/badge/license-LGPL%20v2.1-blue)  
![docs](https://img.shields.io/badge/docs-available-brightgreen)  
<!-- Add code coverage, CI/CD, PyPI, conda-forge badges when available -->

---

![B-vista banner](docs/assets/banner.png) <!-- Optional hero image -->

**B-vista** is a powerful full-stack **EDA assistant** that helps you explore, clean, and visualize your pandas DataFrames — through a rich, browser-based interface with real-time sync and deep statistical insight.

Whether you're a data scientist working solo or a team collaborating over complex datasets, B-vista is designed for **clarity**, **interactivity**, and **scale**.

---

> 🧠 **Key Capabilities**
- Built for large, messy datasets
- Notebook-native (Jupyter, JupyterLab, Colab)
- Web app & API-first flexibility
- Real-time updates with WebSockets
- Deep pandas integration

---

## 📚 Contents

- [✨ Features](#-features)
- [🚀 Quickstart](#-quickstart)
- [📦 Installation](#-installation)
- [🛠️ Environment & Compatibility](#️-environment--compatibility)
- [📘 Documentation](#-documentation)
- [📈 Usage Examples](#-usage-examples)
- [💡 In the News](#-in-the-news)
- [🔗 Related Resources](#-related-resources)
- [🧑‍💻 Developer Setup](#-developer-setup--contributing)
- [📂 Project Structure](#-project-structure)
- [🤝 Contributing](#-contributing)
- [🔖 Versioning](#-versioning)
- [📄 License](#-license)

---

## ✨ Features

- **📈 Descriptive Statistics** — Count, mean, std, min/max, percentiles
- **📊 Correlation Matrix** — Pearson/Spearman heatmaps for numerical columns
- **📉 Distribution Analysis** — Histograms, KDEs, and boxplots
- **🧼 Missing Data Detection** — MCAR, MAR, NMAR categorization & visuals
- **🛠️ Data Cleaning** — Impute with interpolation, mean/median/mode, or custom logic
- **🔁 Data Transformation** — Normalize, standardize, rename, and cast columns
- **📂 CSV Uploads** — Drag-and-drop via browser or via API
- **📡 Real-time Sync** — Powered by Flask-SocketIO
- **🧪 Notebook Integration** — Launch from a Jupyter cell with `bvista.show(df)`
- **🌐 Web-Based Interface** — Beautiful React/Vite frontend with live charts

> 🧠 [Full Feature Reference →](docs/features.md)

---

## 🚀 Quickstart

### 🧪 From a Notebook

```python
import pandas as pd
import bvista

df = pd.read_csv("your_data.csv")
bvista.show(df)
```

### 💻 Local Development Server

```bash
git clone https://github.com/Baci-Ak/b-vista.git
cd b-vista

python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install -e .

python backend/app.py
```

In another terminal tab:

```bash
cd frontend
npm install
npm start
```

Then open:
📍 http://localhost:3000 (frontend)  
📍 http://localhost:5050 (backend)

---

## 📦 Installation

### 🔹 Option 1: Editable Install (Recommended)

```bash
git clone https://github.com/Baci-Ak/b-vista.git
cd b-vista
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install -e .
```

> See [Frontend Setup →](docs/usage/web_interface.md)

---

### 🔹 Option 2: Conda (Optional)

```bash
conda create -n bvista python=3.10
conda activate bvista
pip install -r requirements.txt
pip install -e .
```

---

### 🔹 Option 3: PyPI *(Coming soon)*

```bash
pip install bvista
```

---

### 🔹 Option 4: Docker *(Planned)*

One-line container deployment in development — stay tuned!

---

## 🛠️ Environment & Compatibility

| Tool      | Version            |
|-----------|--------------------|
| Python    | 3.7+ (tested on 3.10) |
| Node.js   | ^18.x              |
| npm       | ^9.x               |

### 🧩 Common Setup Fixes

- `npm start` fails:
  ```bash
  rm -rf node_modules package-lock.json
  npm install
  ```

- Port conflict? Free `3000` or `5050`:
  ```bash
  lsof -i :5050 && kill -9 <PID>
  ```

- Flask server not reachable? Restart `backend/app.py`

---

## 📘 Documentation

🗂️ Everything lives in the [`/docs`](docs) folder.

| Section | Description |
|--------|-------------|
| [Getting Started](docs/getting_started.md) | Beginner guide |
| [Installation](docs/installation.md) | Editable, Conda, PyPI setup |
| [Web Interface](docs/usage/web_interface.md) | Full UI overview |
| [Notebook Integration](docs/usage/jupyter_notebook.md) | Jupyter workflows |
| [API Endpoints](docs/usage/api_endpoints.md) | REST routes |
| [WebSocket Events](docs/usage/websocket_events.md) | Real-time interactions |
| [EDA Features](docs/features.md) | All supported data tools |
| [Dev Architecture](docs/development/architecture.md) | How the app works |

---

## 📈 Usage Examples

### Launch from Notebook

```python
import pandas as pd
import bvista
df = pd.read_csv("data.csv")
bvista.show(df)
```

### Upload via API

```bash
curl -X POST http://localhost:5050/api/upload \
     -F 'file=@your_file.csv'
```

### Trigger a WebSocket update

```python
socketio.emit("data_update", {"status": "DataFrame updated"})
```

---

## 💡 In the News / Inspiration

> “B-vista solves the ‘static DataFrame’ problem. You upload a dataset — and magic happens. Real-time stats, rich visualizations, interactivity. It just works.”  
> — Data Science Beta Tester

- Inspired by tools like **D-Tale**, **Lux**, **pandas-profiling**
- Designed from scratch for **clarity, control, and custom workflows**
- Feedback-driven development from data teams & notebook users

---

## 🔗 Related Resources

- [pandas](https://pandas.pydata.org/)
- [D-Tale (Peer Tool)](https://github.com/man-group/dtale)
- [Lux (Visual Assistant)](https://github.com/lux-org/lux)
- [Flask-SocketIO](https://flask-socketio.readthedocs.io/)
- [Vite (Frontend bundler)](https://vitejs.dev/)
- [Plotly (Charts)](https://plotly.com/python/)

---

## 🧑‍💻 Developer Setup & Contributing

### Run Backend

```bash
cd backend
python app.py
```

### Run Frontend

```bash
cd frontend
npm install
npm start
```

---

## 📂 Project Structure

```text
📦 b-vista
├── backend/            → Flask API, WebSocket events, EDA models
├── frontend/           → React + Vite interface
├── bvista/             → Python integration (Jupyter, CLI)
├── docs/               → Markdown docs
├── datasets/           → Sample data
├── tests/              → Unit + integration tests
├── requirements.txt
├── setup.py
└── README.md
```

---

## 🤝 Contributing

We 💛 community contributions!

Start with:

- [Contributing Guide](docs/development/contributing.md)
- Dev environment instructions
- PR templates (coming soon)
- Linting & test configs

> GitHub Actions CI/CD in progress

---

## 🔖 Versioning

B-vista follows **Semantic Versioning**: [semver.org](https://semver.org)

- **Current version**: `v0.1.0` (Pre-release)
- Expect breaking changes before `v1.0.0`

---

## 📄 License

**B-vista** is open-source under the [GNU LGPL v2.1 License](LICENSE).

> Fork freely. Build boldly. Credit kindly 🙏

---


