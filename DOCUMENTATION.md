# 📘 B-Vista
![Untitled design (8)](https://github.com/user-attachments/assets/e146c080-77cf-4477-8f96-16b56d563dbc)

> Visual, Scalable, and Real-Time Exploratory Data Analysis for pandas DataFrames.

B-Vista is a high-performance EDA (Exploratory Data Analysis) toolkit that connects your `pandas` DataFrame to a dynamic, modern browser UI powered by Flask and WebSockets. Ideal for Jupyter notebooks, Google Colab, Kaggle, or standalone use.

---

## 🔧 Getting Started

### Installation

Install via PyPI:
```bash
pip install bvista
```

Or via Conda:
```bash
conda install -c conda-forge bvista
```

---

### Launch in Notebook

```python
import bvista
import pandas as pd

df = pd.read_csv("your_dataset.csv")
bvista.show(df)
```

By default, B-Vista will auto-launch a backend server and open the interface inline (Jupyter) or in the browser.

---

## 🌟 Core Concepts

### Sessions
Each DataFrame uploaded creates a **unique session**. Sessions are isolated, reusable, and persistent while the backend is alive.

### Backend Auto-Start
B-Vista auto-launches a Flask server the first time you call `bvista.show(df)`. No extra configuration needed.

### Notebook vs Browser
- In **Jupyter/Colab**, B-Vista embeds via iframe.
- In **Python scripts or terminals**, the default is to open in your system browser.

---

## 📊 Main Function: `bvista.show()`

```python
bvista.show(
    df,                  # pandas DataFrame
    name=None,           # Optional session name
    session_id=None,     # Reconnect to previous session
    open_browser=True,   # Force open in web browser
    silent=False         # Suppress logs
)
```

### Examples
```python
bvista.show(df)

bvista.show(df, name="marketing_campaign")

bvista.show(session_id="abc123")  # Reconnect to saved session
```

---

## 🔄 Session Management

### Upload New Dataset
Each call to `show(df)` creates a new session unless a `session_id` is provided.

### Reconnect to Old Session
```python
bvista.show(session_id="session_id_you_saved")
```

---

## 💡 Key Features

B-Vista gives you:
- Descriptive statistics (skew, kurtosis, normality)
- Correlation heatmaps (7+ methods)
- Distributions with auto binning + log scaling
- Missing value visualizations (matrix, heatmap, MCAR/MAR/NMAR diagnostics)
- Smart cleaning tools (mean/mode/knn/autoencoder...)
- Column transforms (rename, reorder, format)
- Duplicate detection and resolution
- Cell-level editing with real-time WebSocket sync

> 🔍 [See full  breakdown →](docs/features.md)

---

## 📒 API Reference

### `bvista.show()`
Launches the UI interface. Must pass either:
- A pandas DataFrame (`df`), or
- A session ID (`session_id`)

### `bvista.start_backend()`
Programmatically start the backend server if needed.

```python
from bvista.server_manager import start_backend
start_backend()
```

---

## 📎 Integration

### Google Colab
```python
!pip install bvista --quiet
import bvista, pandas as pd
df = pd.read_csv("...")
bvista.show(df)
```

### Kaggle
Works out-of-the-box. Use same pattern as Colab.

---

## 🛠️ Troubleshooting

| Issue                                | Fix                                                                 |
|-------------------------------------|----------------------------------------------------------------------|
| Backend failed to start             | Ensure port 5050 is free. Restart kernel.                           |
| Browser doesn't open                | Set `open_browser=True` or open `http://localhost:5050` manually.   |
| Nothing displays in iframe (Colab)  | Try `bvista.show(..., open_browser=True)` to open in full browser. |
| Port already in use                 | Kill other apps on port 5050 or change via env var `BVISTA_PORT`.   |

---

## 🛋️ Deployment

### Docker Usage
```bash
docker pull baciak/bvista:latest
docker run --platform linux/amd64 -p 8501:5050 baciak/bvista:latest
```
Then visit `http://localhost:8501` in your browser.

---

## 🔹 Final Notes

- [Source:](https://github.com/Baci-Ak/b-vista)
- [PyPI:](https://pypi.org/project/bvista)
- [Docker:](https://hub.docker.com/r/baciak/bvista)
- [License:](LICENSE)

---

> ✨ consider starring the repo or sharing with your team!
