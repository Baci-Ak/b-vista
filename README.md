# 📊 B-vista

> **Exploratory Data Analysis tool. Built for scale, clarity, and real-time workflows.**

<!-- Placeholder for logo or product screenshot -->
<!-- ![B-vista banner](docs/assets/banner.png) -->

---

**B-vista** is a full-stack interactive Exploratory Data Analysis (EDA) tool that pairs a Python (Flask) backend with a modern React frontend — built specifically for working with **pandas DataFrames**. It enables users to explore, clean, analyze, and transform data through a rich visual interface, with **real-time updates** and **deep statistical insight**.

Currently, B-vista supports:
- `pandas.DataFrame` objects
- Notebook-native integration (Jupyter, Colab)
- Local or hosted web-based usage


Whether you’re working in a Jupyter notebook or launching a live web session, B-vista gives you deep control over your data — from statistical summaries to real-time collaboration and missing data diagnostics, etc.

---

> 🛠️ Built with: Python · Flask · WebSockets · React · ECharts · Plotly · Pandas · NumPy



---

## ✨ Features

<!-- Placeholder for an animated GIF or UI walkthrough -->
<!-- ![B-vista in action](docs/assets/overview-demo.gif) -->

- **📈 Descriptive Statistics**
  - Instantly view count, mean, std, min, max, percentiles, and more for all numeric columns.

- **📊 Correlation Matrix**
  - Visualize Pearson/Spearman correlation across all numerical features, with heatmap-style UI.

- **📉 Distribution Analysis**
  - Generate histogram, KDE, and box plot visualizations of column distributions.

- **🧼 Missing Data Analysis**
  - Detect and categorize missingness (MCAR, MAR, NMAR) with built-in visual diagnostics.

- **🛠️ Data Cleaning & Imputation**
  - Clean your DataFrame using forward fill, backward fill, interpolation, mean/median/mode, or custom logic.

- **🔁 Data Transformation**
  - Apply column-level operations (standardization, normalization, type casting, etc.)

- **📡 Real-time Sync**
  - WebSocket-powered updates for collaborative usage or multiple views into the same data.

- **🧪 Notebook Integration**
  - Call `bvista.show(df)` to launch the B-vista interface directly inside Jupyter or Colab.

- **📂 File Handling**
  - Upload CSVs or interactively manage DataFrames without restarting your Python session.

- **🌐 Web-based UI**
  - Full React-based interface with tabs, sidebar navigation, dynamic tables, and customizable themes.

<!-- Placeholder for static feature screenshots -->
<!-- ![Feature: correlation](docs/assets/feature-correlation.png) -->
<!-- ![Feature: missing data](docs/assets/feature-missing.png) -->
<!-- ![Feature: interactive cleaning](docs/assets/feature-cleaning.png) -->



















```
---

## 🚀 Quickstart

> The easiest way to explore your pandas DataFrame in a beautiful, interactive interface.

---

### 🧪 From a Notebook

```python
import pandas as pd
import bvista as bv

df = pd.read_csv("your_data.csv")
bv.show(df)  # This launches B-vista in your browser or inside your notebook
```

📌 Works in:
- Jupyter Notebook
- JupyterLab
- Google Colab (Coming soon: screenshots & hosted demo)

---

### 🖥️ From the Command Line (Local Server)

```bash
# Clone the repo
git clone https://github.com/Baci-Ak/b-vista.git
cd b-vista

# (Optional) Create a virtual environment
python3 -m venv venv
source venv/bin/activate  # Or use 'venv\Scripts\activate' on Windows

# Install dependencies
pip install -r requirements.txt

# Launch the backend
python backend/app.py
```

Then open your browser at:  
🔗 [http://localhost:5050](http://localhost:5050)

---

> 📸 **[Placeholder for screenshot or GIF of interface launching]**
```

---



```
---

## 📦 Installation

### 🔹 Option 1: Install from PyPI *(Coming soon)*

```bash
pip install bvista
```

> 🚧 This feature will be available when B-vista is published to PyPI. For now, use option 2 below.

---

### 🔹 Option 2: Run from Source (Developer Mode)

```bash
# Clone the repository
git clone https://github.com/Baci-Ak/b-vista.git
cd b-vista

# (Optional) Set up a virtual environment
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Launch backend server
python backend/app.py
```

> 💡 You must also have the frontend built and served correctly. See the [Frontend Setup Guide](docs/usage/web_interface.md) for full details.

---

### 🐳 Option 3: Docker Support *(Planned)*

> 📦 Docker support is currently under development. Future versions will allow one-line container deployment with pre-built backend + frontend.

---

> 📸 **[Placeholder for screenshot or diagram of installation flow]**
```

---









---

## 📚 Documentation & Guides

The full documentation for B-vista is structured into modules and guides in the [`docs/`](./docs) folder. Below are some key starting points:

- 🔰 [Getting Started Guide](docs/getting_started.md)
- 🚀 [Jupyter Notebook Usage](docs/usage/jupyter_notebook.md)
- 🖥️ [Web Interface Overview](docs/usage/web_interface.md)
- 🔌 [API Endpoints](docs/usage/api_endpoints.md)
- 📡 [WebSocket Events](docs/usage/websocket_events.md)
- 🧪 [EDA Modules Overview](docs/features.md)
- 🛠️ [Development Setup](docs/development/architecture.md)

> 📸 **[Placeholders for GIFs or screenshots of docs navigation]**










```
---

## 🧑‍🏫 Usage Examples

### 🔹 1. Launching B-vista in a Notebook

```python
import pandas as pd
import bvista

df = pd.read_csv("Advertising.csv")
bvista.show(df)
```

🔍 This will:
- Spin up a local B-vista server (via Flask)
- Open an interactive frontend interface
- Connect via WebSockets for real-time sync

> 📸 **[Placeholder for screenshot of the UI launched from notebook]**

---

### 🔹 2. Backend API Endpoint Example

```bash
# Upload a file via backend API (POST)
curl -X POST http://localhost:5050/api/upload \
  -F 'file=@/path/to/your/file.csv'
```

Or fetch column stats:
```bash
curl http://localhost:5050/api/data/summary
```

> 🧠 All API endpoints are documented [here](docs/usage/api_endpoints.md)

---

### 🔹 3. Real-time Socket Events (Advanced)

```python
# Custom WebSocket event trigger (example from event_handlers.py)
socketio.emit("data_update", {"status": "DataFrame updated"})
```

This powers:
- Real-time dashboard refresh
- Reactive UI updates
- Notebook ↔ frontend synchronization

> 📡 See [WebSocket Events](docs/usage/websocket_events.md) for full details.
```

---









```
---

## 🧑‍💻 Developer Setup & Contributing

Want to contribute? Here’s how to run the full stack in development mode:

---

### 🧩 Backend (Flask + WebSockets)

```bash
# From project root
cd backend

# Start backend server
python app.py
```

- Serves at: `http://localhost:5050`
- WebSocket events handled via `socketio` (`backend/websocket`)
- RESTful API routes in: `backend/routes/data_routes.py`
- Core logic in: `backend/models/`

---

### 🖼️ Frontend (React + ECharts)

```bash
# From project root
cd frontend

# Install dependencies
npm install

# Start dev server
npm start
```

- Runs at: `http://localhost:3000`
- Connects to Flask backend via `http://localhost:5050`
- Main app entry point: `frontend/src/App.js`
- Pages located in: `frontend/src/pages`
- Shared components: `frontend/src/components`

> 💡 Uses [Vite](https://vitejs.dev/) for lightning-fast hot module reloads and bundling.

---

### 📂 File Structure Highlights

```text
📦 b-vista
├── backend              → Flask API, WebSocket, Data Logic
├── frontend             → React App (Vite-powered)
├── bvista               → Python library wrapper for notebook integration
├── docs                 → Markdown documentation system
├── tests                → Unit & integration tests
├── datasets             → Sample data for demos or testing
```

---

### ✅ Contributing

We welcome contributions! Please see [docs/development/contributing.md](docs/development/contributing.md) for:

- Branching strategy
- Code style guidelines
- Pull request checklists
- Testing instructions

---

> 🧪 **Coming soon:** pre-commit hooks, GitHub Actions CI/CD, unit test coverage, issue templates, and more.

> 📸 **[Placeholder: dev environment diagram or GIF of live reload in action]**
```

---
