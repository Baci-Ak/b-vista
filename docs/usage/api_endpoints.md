# 📡 API Endpoints

The B-vista backend exposes a set of **RESTful API endpoints** that allow programmatic interaction with uploaded datasets, summaries, and session management. These endpoints are useful for frontend communication, integration with external tools, or advanced usage beyond the notebook.

---

## 🔐 Base URL

All endpoints are served via:

```text
http://localhost:5050/api/
```

> Adjust accordingly if hosted remotely.

---

## 📁 Upload Data

### `POST /api/upload`

Uploads a new dataset to the backend. Used by the notebook integration and UI upload flow.

#### Request
- **Method**: `POST`
- **Content-Type**: `multipart/form-data`
- **Fields**:
  - `file`: CSV or Pickle file
  - `name`: Name of the dataset (optional)
  - `session_id`: Unique session ID (optional)

#### Example
```bash
curl -X POST http://localhost:5050/api/upload \
  -F 'file=@/path/to/data.csv'
```

#### Response
```json
{
  "status": "success",
  "session_id": "your_session_id"
}
```

---

## 📊 Get Summary Statistics

### `GET /api/data/summary`

Returns descriptive statistics (mean, std, percentiles, etc.) for all numeric columns.

#### Example
```bash
curl http://localhost:5050/api/data/summary
```

#### Response
```json
{
  "summary": {
    "column_1": {"mean": 4.2, "std": 0.3, ...},
    "column_2": {...}
  }
}
```

---

## 📉 Get Distribution Data

### `GET /api/data/distribution/<column_name>`

Returns histogram, KDE, and box plot-ready values for a specific column.

#### Example
```bash
curl http://localhost:5050/api/data/distribution/age
```

#### Response
```json
{
  "histogram": [...],
  "kde": [...],
  "box": {
    "min": 12,
    "q1": 18,
    "median": 22,
    "q3": 30,
    "max": 45
  }
}
```

---

## 📌 Get Column Correlations

### `GET /api/data/correlation`

Returns a Pearson and Spearman correlation matrix for numerical features.

#### Example
```bash
curl http://localhost:5050/api/data/correlation
```

---

## 🧼 Get Missing Data Info

### `GET /api/data/missing`

Returns missing data counts, percentage, and type inference (MCAR/MAR/etc.).

#### Example
```bash
curl http://localhost:5050/api/data/missing
```

---

## 🧠 Session Management

### `GET /api/get_sessions`
Returns a dictionary of active sessions.

### `GET /api/session/<session_id>`
Gets metadata for a specific session.

---

## 🔄 Reload/Reset Data

### `POST /api/reload`
Reloads the most recent dataset or resets session state.

---

## 🔌 Custom / Advanced

These are only exposed if certain features/modules are enabled:

- `POST /api/data/clean`
- `POST /api/data/transform`

> See respective module docs for body schema and examples.

---

## 🐞 Error Responses

All failed requests return a consistent error format:

```json
{
  "status": "error",
  "error": "Description of what went wrong."
}
```

---

## 🔗 Related Docs

- 📁 [Getting Started](../getting_started.md)
- 🧪 [Notebook Usage](jupyter_notebook.md)
- 🖥️ [Web UI Guide](web_interface.md)
- 📡 [WebSocket Events](websocket_events.md)

