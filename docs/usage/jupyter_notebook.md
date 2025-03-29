# 📓 Jupyter Notebook Integration

B-vista provides **seamless integration** with Jupyter environments — including Jupyter Notebook, JupyterLab, and (soon) Google Colab. With a single function call, you can launch the full B-vista interface and interactively explore your `pandas` DataFrame without leaving your notebook.

---

## ⚙️ Prerequisites

Make sure you've installed B-vista via one of the methods below:

```bash
# (Recommended during development)
git clone https://github.com/Baci-Ak/b-vista.git
cd b-vista
pip install -r requirements.txt
pip install -e .    # Install in editable mode

```

Then ensure you can import B-vista:

```python
import bvista
```

> 📌 Python ≥ 3.7 is required. Tested on Python 3.10+

---

## 🚀 Basic Usage

```python
import pandas as pd
import bvista

df = pd.read_csv("your_dataset.csv")
bvista.show(df)
```

- Automatically launches B-vista in your **default browser**
- Opens a fully interactive UI connected to your DataFrame
- Works inside **notebooks**, **terminals**, or **scripts**

---

## 🔍 Behind the Scenes

When you call:

```python
bvista.show(df)
```

Here's what happens under the hood:

1. ✅ **Backend Check**: Verifies if Flask backend is already running on `http://localhost:5050`.
2. 🧠 **Session Inference**: If no name is passed, it tries to auto-detect the DataFrame variable name.
3. 📦 **Serialization**: Converts your DataFrame to a `.pkl` file and uploads it to the backend.
4. 🌐 **Web Launch**: Opens the interactive UI in a browser window (or iframe inside notebook).

---

## 🖼️ Notebook Display Example

The interface is rendered **inside the notebook** using an HTML iframe:

```python
<iframe src="http://localhost:5050/?session_id=Advertising" width="100%" height="600px"></iframe>
```

You’ll also get a link to open it in a standalone browser tab.

> 📸 **[Placeholder: Screenshot of embedded UI inside notebook]**

---

## 🧠 Advanced Parameters

```python
bvista.show(df, name="MyDataset", session_id="session123")
```

- `df`: Required if uploading a new DataFrame
- `name`: Optional name for the dataset (defaults to variable name)
- `session_id`: Use a specific session instead of uploading new data

---

## 🛡️ Error Handling

The `bvista.show()` function performs multiple checks:

| Scenario                              | Behavior                                                        |
|---------------------------------------|-----------------------------------------------------------------|
| Backend not running                   | Raises `ConnectionError` with clear message                     |
| Invalid session_id                    | Raises `ValueError` for missing or bad session                  |
| Upload failed                         | Raises `ValueError` with backend error message                  |
| DataFrame missing or invalid type     | Raises `ValueError` if `df` is not a pandas DataFrame           |

---

## 🧪 Auto Backend Start (Optional)

By default, importing `bvista` **auto-starts the backend** via:

```python
from .server_manager import start_backend
```

This is triggered in `bvista/__init__.py`:

```python
from .notebook_integration import show
from .server_manager import start_backend
start_backend()  # ✅ Auto-start backend if not already running
```

> ✅ Useful for standalone notebooks or demo environments.

---

## ✅ Successful Launch

Once launched, you can:

- Explore all EDA modules visually
- Upload additional CSVs
- Monitor WebSocket-powered real-time updates
- Switch between datasets

> 🎥 **[Placeholder: GIF showing end-to-end notebook launch]**

---

## 🐞 Troubleshooting

| Problem                      | Fix                                                                 |
|-----------------------------|----------------------------------------------------------------------|
| Backend not found error     | Manually start with `python backend/app.py`                          |
| Port already in use         | Free up port `5050`: `lsof -i :5050 && kill -9 <PID>`                |
| WebSocket not connecting    | Ensure both frontend (`:3000`) and backend (`:5050`) are active      |
| Notebook display is blank   | Try opening in browser: `http://localhost:5050/?session_id=...`      |

---

## 🔗 Related Docs

- 📁 [Getting Started](../getting_started.md)
- 🖥️ [Web Interface Guide](web_interface.md)
- 🔌 [API Reference](api_endpoints.md)
- 📡 [WebSocket Events](websocket_events.md)

---

> 💬 Need help? [Open an issue](https://github.com/Baci-Ak/b-vista/issues) or join the discussion!

```

---