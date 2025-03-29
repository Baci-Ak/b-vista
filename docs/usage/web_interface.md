# 🖥️ Web Interface Guide

The B-vista web interface is a **modern, interactive, browser-based UI** built using React, ECharts, and Plotly. It connects seamlessly to the Flask backend and enables users to explore, clean, and visualize data from uploaded CSVs or notebook sessions.

This guide explains the structure, layout, and usage of the web interface.

---

## 🌐 Accessing the Web UI

Once the backend is running (`python backend/app.py`) and the frontend is launched (`npm start` inside `frontend/`), open your browser at:

```http
http://localhost:3000
```

> 📌 When launched via notebook (`bvista.show(df)`), it auto-opens `http://localhost:5050/?session_id=...`

---

## 🧱 Interface Layout

The UI is composed of:

| Section       | Description                                                                 |
|---------------|-----------------------------------------------------------------------------|
| Sidebar       | Left-hand vertical navigation. Contains tabs/modules like Overview, Stats, Cleaning, Correlation, etc. |
| Top Bar       | Displays current session, dataset name, and options for theme or refresh.  |
| Main Content  | Displays current module (e.g., summary stats, correlation matrix, data table, etc.) |

The layout is implemented in `Layout.js`, `Sidebar.js`, and `App.js`.

---

## 📂 Loading Data

There are two main ways to load data into B-vista:

### 🔹 1. From Notebook

Calling `bvista.show(df)` in Python auto-uploads the DataFrame and opens the web interface.

### 🔹 2. Uploading CSV via UI

1. Click on the upload area or drag a `.csv` file.
2. File is sent to backend (`/api/upload`)
3. WebSocket event notifies UI to refresh the session.

See upload handling logic in `data_routes.py` and `file_handler.py`.

---

## 📊 Key Modules & Tabs

Each tab on the sidebar corresponds to a functional module:

### 📈 Summary Statistics
- Renders count, mean, median, standard deviation, etc.
- Displayed using styled tables (`DataTable.js`)

### 📉 Distributions
- Histograms, KDEs, and box plots per column.
- Powered by Plotly.js and ECharts.

### 📊 Correlation Matrix
- Heatmap of pairwise Pearson/Spearman correlation coefficients.
- Implemented in `CorrelationMatrix.js` with styling from `CorrelationMatrix.css`

### 🧼 Missing Data
- Visual diagnosis of MCAR/MAR/NMAR values.
- Highlights patterns of missingness and offers cleaning options.

### 🛠️ Data Cleaning
- Imputation via mean/median/mode, interpolation, forward/backward fill.
- Column selector + dropdown controls.

### 🔁 Data Transformation
- Normalize, standardize, or cast types.
- Apply operations to selected columns with preview.

### 📋 Raw Table View
- Interactive, editable data table (`DataTable.js` + `CellEditor.js`)
- Supports sorting, pagination, and in-place editing

---

## 🔌 API Integration

The UI communicates with the backend via:

- **RESTful Endpoints** — `/api/data/summary`, `/api/data/correlation`, etc.
- **WebSocket Events** — Receives real-time updates via `socket.io`

This ensures real-time syncing of data between views or users.

---

## ⚙️ Customization & Themes

- Theme switcher (light/dark)
- Column selector
- Toggle chart types (histogram, box, KDE)
- Responsive layout for mobile/tablet

> 📌 You can modify the layout and themes in `Layout.css`, `Sidebar.css`, and component-specific CSS files.

---

## 🧪 Dev Tips

- React app is bootstrapped with [Vite](https://vitejs.dev/)
- Use browser dev tools to inspect requests and components
- WebSocket logs appear in browser console
- To debug session issues, visit `/api/get_sessions`

---

## ✅ Summary

The B-vista Web UI provides:

- Fully visual, real-time interaction with your data
- Modular EDA workflows
- Seamless transition between notebook and browser sessions

> 🎯 Tip: Use the web UI to clean/transform data, then sync it back to your notebook or download a CSV.

---

## 🔗 Related Docs

- 📓 [Jupyter Notebook Usage](jupyter_notebook.md)
- 🔌 [API Endpoints](api_endpoints.md)
- 📡 [WebSocket Events](websocket_events.md)

---

> 💬 Feedback or issues? [Open a GitHub issue](https://github.com/Baci-Ak/b-vista/issues) or start a discussion!

