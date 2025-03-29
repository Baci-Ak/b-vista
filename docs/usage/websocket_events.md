---

# 📡 WebSocket Events

B-vista uses **WebSockets** (via `Flask-SocketIO`) to power **real-time updates** between the backend and frontend. This enables seamless interactivity — as data is transformed, filtered, or analyzed, the UI updates instantly across connected sessions.

This guide explains the key WebSocket events used in the app, how they're triggered, and how to listen or emit them.

---

## ⚙️ WebSocket Setup

The WebSocket logic is defined in:

- `backend/websocket/socket_manager.py`
- `backend/websocket/event_handlers.py`

```python
# Inside backend/app.py
from backend.websocket.socket_manager import socketio

# Run Flask-SocketIO server
socketio.run(app, port=5050)
```

The frontend connects via `socket.io-client` on port `5050`.

---

## 🔄 Core Events Overview

| Event Name        | Direction      | Purpose                                         |
|------------------|----------------|-------------------------------------------------|
| `connect`        | Frontend → Backend | On client connection                       |
| `disconnect`     | Frontend → Backend | On client disconnect                        |
| `data_update`    | Backend → Frontend | Notify clients that DataFrame has changed   |
| `session_loaded` | Backend → Frontend | Confirm a session has successfully loaded   |
| `trigger_stats`  | Frontend → Backend | Request computation of descriptive stats    |
| `stats_ready`    | Backend → Frontend | Send computed stats to frontend             |
| `correlation_ready` | Backend → Frontend | Push correlation matrix result            |
| `missing_data_ready` | Backend → Frontend | Push missing data analysis result         |
| `distribution_ready` | Backend → Frontend | Send histogram/distribution data          |

---

## 🔁 Emit from Backend

```python
from flask_socketio import emit

# Example: Notify all connected clients about data update
socketio.emit("data_update", {"status": "updated", "session_id": "abc123"})
```

You’ll find emits like this in `event_handlers.py` after data processing or file upload.

---

## 📥 Emit from Frontend

Frontend emits (usually via `socket.emit(...)`) are used to **request server actions**:

```js
socket.emit("trigger_stats", { session_id: currentSession });
```

Example usages:

- `DataTable.js` → emits `trigger_stats` when table loads
- `DescriptiveStats.js` → listens for `stats_ready`
- `CorrelationMatrix.js` → listens for `correlation_ready`
- `MissingData.js` → listens for `missing_data_ready`

---

## ✅ Example Event Flow

### 🟢 When a new CSV is uploaded:

1. Backend saves the file
2. Backend emits:

```python
emit("data_update", {"status": "uploaded", "session_id": session_id})
```

3. Frontend listens via:

```js
socket.on("data_update", (payload) => {
  if (payload.session_id === currentSession) {
    refreshTable();  // re-fetches table
  }
});
```

---

## 🎯 Best Practices

- Always include a `session_id` in event payloads
- Use `socket.off(...)` to clean up listeners in React useEffect
- Add error handling for timeout/failure cases
- Avoid duplicate emits (e.g., debounce user-triggered events)

---

## 🧪 Debugging Tips

| Symptom                         | Suggestion                                      |
|--------------------------------|-------------------------------------------------|
| No event received               | Check backend logs for `socketio.emit()` calls |
| Frontend not syncing            | Ensure port 5050 is reachable (CORS?)          |
| Duplicate messages              | Clear listeners before re-adding               |
| WebSocket not connecting        | Check `socket.io-client` version compatibility |

---

## 🧠 Advanced Use

You can extend the event model for:

- Broadcast to **specific clients**
- Handle **room-based sessions**
- Support **collaborative editing** via shared sessions

> 📚 See Flask-SocketIO docs: [https://flask-socketio.readthedocs.io](https://flask-socketio.readthedocs.io)

---

## 🔗 Related Files

- `backend/websocket/socket_manager.py`
- `backend/websocket/event_handlers.py`
- `frontend/src/pages/DataTable.js`
- `frontend/src/pages/DescriptiveStats.js`
- `frontend/src/pages/CorrelationMatrix.js`
- `frontend/src/pages/MissingData.js`
- `frontend/src/pages/DistributionAnalysis.js`

---

> 💬 Questions? Open an issue or start a discussion on GitHub.

```

---
