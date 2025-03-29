# 🔧 Feature Overview: EDA Modules in B-vista

B-vista provides a suite of powerful **Exploratory Data Analysis (EDA)** modules for interactive, browser-based inspection of `pandas` DataFrames. These modules are backed by well-defined Python classes and served through API endpoints.

This document summarizes each major feature/module, including its purpose, interface behavior, and backend logic.

---

## 📊 Descriptive Statistics

- **Purpose**: Quickly compute and display basic statistics for numeric columns.
- **Stats**: count, mean, std, min, max, 25%/50%/75% percentiles, null count, dtype.
- **Backend**: `descriptive_stats.py`
- **Endpoint**: `GET /api/data/summary`
- **Frontend Component**: `DescriptiveStats.js`
- **Returns**: JSON summary per column

---

## 📉 Correlation Matrix

- **Purpose**: Visualize pairwise correlation between numerical columns.
- **Types**: Pearson (default), Spearman (optionally supported)
- **Backend**: `correlation.py`
- **Endpoint**: `GET /api/data/correlation`
- **Frontend Component**: `CorrelationMatrix.js`
- **Returns**: correlation matrix in flattened or 2D array format

---

## 🔄 Distribution Analysis

- **Purpose**: Inspect value distribution for each numerical column.
- **Visuals**: Histogram, KDE plot, Box plot
- **Backend**: `distribution_analysis.py`
- **Endpoint**: `GET /api/data/distribution?column=<name>`
- **Frontend Component**: `DistributionAnalysis.js`
- **Returns**: Bin edges, densities, quantiles, etc.

---

## 🚮 Missing Data Analysis

- **Purpose**: Detect and categorize missingness in your data.
- **Types**: MCAR, MAR, NMAR (Heuristic/Pattern-based)
- **Backend**: `missing_data_analysis.py`, `missing_data_types.py`
- **Endpoint**: `GET /api/data/missing`
- **Frontend Component**: `DataTable.js`
- **Returns**: Null counts, missing percentages, pattern clusters

---

## 🛠️ Data Cleaning & Imputation

- **Purpose**: Perform simple cleaning or imputation actions.
- **Options**: `fillna(method)`, `mean`, `median`, `mode`, `ffill`, `bfill`, `interpolate`
- **Backend**: `data_cleaning.py`
- **Endpoint**: `POST /api/data/clean`
- **Frontend Component**: `DataCleaning.js`
- **Payload**:
  ```json
  {
    "column": "age",
    "method": "median"
  }
  ```
- **Returns**: Updated column stats

---

## 🧰 Data Transformation

- **Purpose**: Apply transformations to columns in-place.
- **Options**: Normalize, Standardize, Convert dtype, Scale, Encode
- **Backend**: `data_cleaning.py` (currently handled there)
- **Endpoint**: `POST /api/data/transform`
- **Frontend Component**: `DataCleaning.js`
- **Returns**: Updated column data and stats

> 🔍 **Planned Enhancements**:
> - Feature scaling visualization
> - Undo/redo for column operations

---

## 📦 File Uploads & Session Handling

- **Purpose**: Upload CSV or DataFrame and create session.
- **Backend**: `data_manager.py`
- **Endpoint**: `POST /api/upload`
- **Supported Formats**: CSV (via browser), Pickle (via notebook integration)
- **Session API**:
  - `GET /api/get_sessions`
  - `GET /api/session/<session_id>`

---

## 🔔 Real-Time WebSocket Events

- **Purpose**: Keep frontend in sync across actions
- **Backend**: `event_handlers.py`, `socket_manager.py`
- **Emitted Events**:
  - `data_update`: After cleaning or transformation
  - `file_uploaded`: After new file is parsed
  - `session_changed`: When switching datasets
- **Frontend Usage**: `socket.on("data_update", callback)`

---

## 💡 Future Module Ideas

- PCA/Dimensionality Reduction
- Outlier Detection
- Clustering Overview (KMeans)
- Time Series Decomposition
- Target Leakage Checker

---

## ✨ Summary Table

| Module                 | File                       | Endpoint                      | Frontend Component       |
|------------------------|----------------------------|-------------------------------|---------------------------|
| Descriptive Stats      | `descriptive_stats.py`     | `/api/data/summary`          | `DescriptiveStats.js`     |
| Correlation Matrix     | `correlation.py`           | `/api/data/correlation`      | `CorrelationMatrix.js`    |
| Distribution Analysis  | `distribution_analysis.py` | `/api/data/distribution`     | `DistributionAnalysis.js` |
| Missing Data           | `missing_data_analysis.py` | `/api/data/missing`          | `DataTable.js`            |
| Data Cleaning          | `data_cleaning.py`         | `/api/data/clean`            | `DataCleaning.js`         |
| Data Transformation    | `data_cleaning.py`         | `/api/data/transform`        | `DataCleaning.js`         |
| File Uploads           | `data_manager.py`          | `/api/upload`                | `DataTable.js`            |
| WebSocket Events       | `event_handlers.py`        | (SocketIO)                   | All Modules               |

---

> ✊ This file is kept up to date with all implemented modules. If you're working on a new EDA feature, add it here once backend + frontend support is in place.

