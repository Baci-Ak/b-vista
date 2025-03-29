Great catch! Let’s write the full `docs/installation.md` file now, and I’ll make sure to include **conda installation instructions** as well, along with pip, editable mode, and dev setup. Here's the full, clean version you can use:

---

```md
# 🧰 Installation Guide

Welcome to the installation guide for **B-vista** — a modern, interactive EDA tool that pairs a Python backend with a React frontend. Choose the method that fits your workflow best: PyPI (coming soon), source install, or Conda setup.

---

## 📦 Installation Options

### 🔹 Option 1: Install from PyPI *(Coming Soon)*

Once available, you’ll be able to install B-vista via:

```bash
pip install bvista
```

> 📦 This is the easiest option for users who don't plan to modify the source code.

---

### 🔹 Option 2: Developer Mode (Editable Install)

For contributors or local development:

```bash
git clone https://github.com/Baci-Ak/b-vista.git
cd b-vista

# Optional: create a virtual environment
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install Python dependencies
pip install -r requirements.txt

# Install in editable mode
pip install -e .

# Start the backend
python backend/app.py
```

> ✅ Recommended for real-time development or testing changes to the library.

---

### 🔹 Option 3: Conda Environment Setup

You can also use **Anaconda** or **Miniconda** for environment management:

```bash
# Create a new environment
conda create -n bvista python=3.10

# Activate it
conda activate bvista

# Install dependencies from pip
pip install -r requirements.txt
pip install -e .

# Start the backend
python backend/app.py
```

> 💡 Conda is particularly useful on systems where Python package conflicts are common.

---

## 🖼️ Frontend Setup

The frontend is built using React + Vite. Set it up as follows:

```bash
cd frontend

# Install Node.js dependencies
npm install

# Start the dev server
npm start
```

- Opens at: `http://localhost:3000`
- Connects to backend at: `http://localhost:5050`

> ✅ Requires Node.js `^18.x` and npm `^9.x`

---

## 🐳 Docker (Planned)

B-vista will support Docker deployment in future releases.

Expected flow:

```bash
docker build -t bvista .
docker run -p 5050:5050 bvista

# Coming soon:
docker run baciak/bvista:latest

```




> 🐋 Docker support will allow one-line startup with bundled backend + frontend.
Will include auto-exposing frontend and backend ports

Designed for deployment to cloud or internal servers

🐳 [Placeholder: Link to docker-compose.yml & Dockerfile once available]

---

## ✅ Version Compatibility

| Tool     | Recommended Version |
|----------|----------------------|
| Python   | 3.7 or higher        |
| Node.js  | ^18.x                |
| npm      | ^9.x                 |

> 📌 Check versions with:
```bash
python --version
node -v
npm -v
```

---

## 🛠️ Optional: Notebook Integration

Once installed, you can launch B-vista from a Jupyter notebook:

```python
import bvista
import pandas as pd

df = pd.read_csv("your_data.csv")
bvista.show(df)
```

> 📚 See [Notebook Integration](./usage/jupyter_notebook.md) for more.

---

## 📂 Project Structure Overview

```text
📦 b-vista/
├── backend/         # Flask backend (API + WebSockets)
├── frontend/        # React frontend (Vite-based)
├── bvista/          # Python integration module
├── datasets/        # Example CSVs
├── docs/            # Full documentation (Markdown)
├── tests/           # Unit & integration tests
└── setup.py         # Package configuration
```

---

## 🧪 Common Installation Issues

| Error                                | Fix/Tip                                                                 |
|-------------------------------------|-------------------------------------------------------------------------|
| `npm start` fails                   | Ensure Node.js is v18+, delete `node_modules` and run `npm install`     |
| Backend not starting                | Make sure Python ≥ 3.7, and port 5050 is available                      |
| CSVs failing to upload              | Confirm files are UTF-8 encoded and under size limits                   |
| WebSocket not connecting            | Make sure both backend and frontend are running                         |
| Notebook import error               | Ensure you ran `pip install -e .` inside the `bvista/` root             |

---

## 🧑‍💻 Want to Contribute?

Check the full developer setup in:

📄 [docs/development/architecture.md](../development/architecture.md)  
📄 [docs/development/contributing.md](../development/contributing.md)

---

> 🧠 Need help? Open an issue on [GitHub](https://github.com/Baci-Ak/b-vista/issues) or start a discussion.

```

---

