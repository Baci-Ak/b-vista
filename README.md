
---


# 📊 B-vista

> **Exploratory Data Analysis tool. Built for scale, clarity, and real-time workflows.**

<!-- Placeholder for logo or product screenshot -->
<!-- ![B-vista banner](docs/assets/banner.png) -->

---

**B-vista** is an enterprise-grade interactive Exploratory Data Analysis (EDA) tool — a full-stack application that connects a Python (Flask) backend with a modern React frontend. It empowers data professionals to clean, analyze, transform, and visualize pandas DataFrames through an intuitive, browser-based interface with **real-time updates**, **deep statistical insights**, and seamless **notebook integration**.

Currently supports:
- `pandas.DataFrame` objects
- Jupyter & Colab usage
- Web app sessions (local or hosted)

Whether you're exploring messy datasets, building reports, or collaborating in real-time, B-vista equips you with the tools to do it all — interactively and visually.

---

> 🛠️ Built with: Python · Flask · WebSockets · React · ECharts · Plotly · Pandas · NumPy

---

## ✨ Features

<!-- Placeholder for an animated GIF or UI walkthrough -->
<!-- ![B-vista in action](docs/assets/overview-demo.gif) -->

- **📈 Descriptive Statistics** — Instant statistical summaries (count, mean, std, percentiles, etc.)
- **📊 Correlation Matrix** — Heatmap view of Pearson/Spearman correlations.
- **📉 Distribution Analysis** — Histogram, KDE, and box plots per column.
- **🧼 Missing Data Diagnostics** — Visualize and detect MCAR, MAR, NMAR types.
- **🛠️ Data Cleaning & Imputation** — Interpolation, fill methods, and custom logic.
- **🔁 Data Transformation** — Normalize, standardize, or cast columns in-place.
- **📡 Real-Time Sync** — WebSocket-powered two-way updates.
- **🧪 Notebook Integration** — Launch from Jupyter with a single `bvista.show(df)` call.
- **📂 File Handling** — Upload and manage CSVs interactively.
- **🌐 Web-Based Interface** — Modern, tabbed React UI with live charts and interactions.

<!-- Placeholder screenshots -->
<!-- ![correlation](docs/assets/feature-correlation.png) -->
<!-- ![missing data](docs/assets/feature-missing.png) -->

---

## 🚀 Quickstart

> The easiest way to explore your pandas DataFrame in a beautiful, interactive interface.

### 🧪 From a Notebook

```python
import pandas as pd
import bvista as bv

df = pd.read_csv("your_data.csv")
bv.show(df)
```

📌 Works in:
- Jupyter Notebook
- JupyterLab
- Google Colab *(coming soon)*

---

### 🖥️ From the Command Line (Local Server)

```bash
git clone https://github.com/Baci-Ak/b-vista.git
cd b-vista

python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

pip install -r requirements.txt
python backend/app.py
```

Then open your browser at:  
🔗 [http://localhost:5050](http://localhost:5050)

> 📸 **[Placeholder for GIF of app launch]**

---

## 📦 Installation

### 🔹 Option 1: PyPI *(Coming soon)*

```bash
pip install bvista
```

---

### 🔹 Option 2: From Source (Developer Mode)

```bash
git clone https://github.com/Baci-Ak/b-vista.git
cd b-vista

python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python backend/app.py
```

> 💡 Make sure to set up the frontend as well. See [Frontend Setup](docs/usage/web_interface.md)

---

### 🐳 Option 3: Docker *(Planned)*

One-line container deployment *(coming soon)*.

> 📸 **[Placeholder for architecture screenshot]**

---

## 🛠️ Environment & Compatibility

### ✅ Requirements

- **Python**: `>=3.7`
- **Node.js**: `^18.x`
- **npm**: `^9.x`

### ⚠️ Common Setup Issues

- `npm start` fails: Ensure you're on Node.js v18+. Clear node_modules:
  ```bash
  rm -rf node_modules package-lock.json
  npm install
  ```

- Backend sync problems: Check `5050` is free, CORS config, and both apps are running.

- Large CSV issues: Ensure proper encoding (UTF-8) and sufficient system RAM.

---

> 📸 **[Placeholder: compatibility chart or error gif]**

---

## 📚 Documentation & Guides

📁 See full docs in [`/docs`](./docs)

- 🔰 [Getting Started](docs/getting_started.md)
- 🖥️ [Web UI Guide](docs/usage/web_interface.md)
- 🚀 [Notebook Integration](docs/usage/jupyter_notebook.md)
- 🔌 [API Reference](docs/usage/api_endpoints.md)
- 📡 [WebSocket Events](docs/usage/websocket_events.md)
- 🧪 [EDA Modules](docs/features.md)
- 🛠️ [Dev Architecture](docs/development/architecture.md)

> 📸 **[Placeholder for docs screenshots]**

---

## 🧑‍🏫 Usage Examples

### Notebook Integration

```python
import pandas as pd
import bvista

df = pd.read_csv("Advertising.csv")
bvista.show(df)
```

### API: Upload a file

```bash
curl -X POST http://localhost:5050/api/upload \
  -F 'file=@/path/to/your/file.csv'
```

### API: Summary stats

```bash
curl http://localhost:5050/api/data/summary
```

### WebSocket: Trigger event

```python
socketio.emit("data_update", {"status": "DataFrame updated"})
```

> See more in [API Docs](docs/usage/api_endpoints.md) and [WebSockets](docs/usage/websocket_events.md)

---

## 🧑‍💻 Developer Setup & Contributing

### Backend

```bash
cd backend
python app.py
```

- Serves: `http://localhost:5050`
- WebSocket: `backend/websocket/`
- API: `backend/routes/data_routes.py`

---

### Frontend

```bash
cd frontend
npm install
npm start
```

- Runs: `http://localhost:3000`
- Entry: `src/App.js`
- Components: `src/components/`, `src/pages/`

> Uses **Vite** for lightning-fast development.

---

### Project Structure

```text
📦 b-vista
├── backend              # Flask + WebSocket
├── frontend             # React + Vite
├── bvista               # Python notebook integration
├── docs                 # Full documentation
├── datasets             # Sample data
├── tests                # Unit & integration tests
```

---

### Contributing

We welcome contributions! See:

📄 [Contributing Guide](docs/development/contributing.md)

- Branch strategy
- Code style
- PR checklist
- Testing instructions

> 🧪 CI/CD with GitHub Actions coming soon.

---

## 🔖 Versioning

Follows [Semantic Versioning](https://semver.org/).  
**Current version**: `v0.1.0` *(Pre-release)*

---

## 📄 License

<!-- ![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg) -->

Licensed under the [MIT License](LICENSE).

> 🙌 Contributions welcome — just credit and enjoy.

---
```

---
