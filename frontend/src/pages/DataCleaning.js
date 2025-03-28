// frontend/src/pages/DataCleaning.js
import React, { useEffect, useState, useRef } from "react";
import axios from "axios";
import { AgGridReact } from "ag-grid-react";
import "ag-grid-community/styles/ag-grid.css";
import "ag-grid-community/styles/ag-theme-alpine.css";
import "./DataCleaning.css";

const API_URL = "http://127.0.0.1:5050";

const DataCleaning = () => {
  const [sessions, setSessions] = useState([]);
  const [selectedSession, setSelectedSession] = useState(null);
  const [datasetShape, setDatasetShape] = useState("(0, 0)");
  const [columnDefs, setColumnDefs] = useState([]);
  const [rowData, setRowData] = useState([]);
  const [columns, setColumns] = useState([]);
  const gridRef = useRef(null); // Add this near useState

  const [selectedColumns, setSelectedColumns] = useState([]);
  const [cleaningMethod, setCleaningMethod] = useState("dropna");
  const [showColumnDropdown, setShowColumnDropdown] = useState(false);
  const [searchTerm, setSearchTerm] = useState("");
  const dropdownRef = useRef(null);
  const [showMethodDropdown, setShowMethodDropdown] = useState(false);
  const methodDropdownRef = useRef(null);
  const [cleaningMessage, setCleaningMessage] = useState("");
  const [showToast, setShowToast] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [showMethodTooltip, setShowMethodTooltip] = useState(false);
  const [tooltipText, setTooltipText] = useState("");



  const cleaningMethods = [
    { label: "🧹 Drop Missing", value: "dropna" },
    { label: "➕ Fill with Mean", value: "mean" },
    { label: "🧮 Fill with Median", value: "median" },
    { label: "📊 Fill with Mode", value: "mode" },
    { label: "➡️ Forward Fill", value: "forward_fill" },
    { label: "⬅️ Backward Fill", value: "backward_fill" },
    { label: "🔁 Interpolate (Linear)", value: "interpolation" },
    { label: "🧵 Interpolate (Spline)", value: "spline" },
    { label: "📐 Interpolate (Poly)", value: "polynomial" },
    { label: "🤖 KNN Impute", value: "knn" },
    { label: "🧠 Iterative (MICE)", value: "iterative" },
    { label: "📈 Regression Impute", value: "regression" },
    { label: "🧬 Autoencoder (Deep Learning)", value: "autoencoder" },

  ];
  
  



  // ✅ Tooltip state and descriptions

  const methodDescriptions = {
    dropna: "Drops all rows that contain missing values in selected columns.",
    mean: "Fills missing values using the column-wise average (mean).",
    median: "Fills missing values using the median value of each column.",
    mode: "Fills missing values with the most frequent value (mode) per column.",
    forward_fill: "Fills missing values with the last known value before it.",
    backward_fill: "Fills missing values using the next available value after it.",
    interpolation: "Performs linear interpolation between known data points.",
    spline: "Applies spline interpolation for smoother curve-fitting imputation.",
    polynomial: "Interpolates using a polynomial curve (default: quadratic).",
    knn: "Uses K-Nearest Neighbors to estimate and fill missing numeric values.",
    iterative: "Iteratively models each feature using other features (MICE).",
    regression: "Predicts missing values using multivariate linear regression.",
    autoencoder: "Uses a neural network to learn data structure and impute values."
  };
  

  
  
  
  
  
  
  // ✅ Fetch sessions
  useEffect(() => {
    const fetchSessions = async () => {
      const res = await axios.get(`${API_URL}/api/sessions`);
      const entries = Object.entries(res.data.sessions).map(([id, session]) => ({
        id,
        name: session.name || `Dataset ${id}`,
      }));
      setSessions(entries);
      if (entries.length && !selectedSession) {
        setSelectedSession(entries[entries.length - 1].id);
      }
    };
    fetchSessions();
  }, [selectedSession]);




  const fetchSessionData = async (sessionId) => {
    const res = await axios.get(`${API_URL}/api/session/${sessionId}`);
    const { data, columns, total_rows, total_columns } = res.data;
  
    setRowData(data);
    setColumnDefs(columns.map(col => ({
      field: col.field,
      headerName: col.headerName,
      resizable: true,
      sortable: true,
      filter: true
    })));
  
    const colOptions = columns.map(col => ({ label: col.headerName, value: col.field }));
    setColumns(colOptions);
    setSelectedColumns(colOptions);
    setDatasetShape(`(${total_rows}, ${total_columns})`);
  };
  




  // ✅ Fetch data + shape
  useEffect(() => {
    if (selectedSession) {
      fetchSessionData(selectedSession);
    }
  }, [selectedSession]);
  

  // ✅ Close dropdowns when clicking outside
  useEffect(() => {
    const closeDropdowns = (e) => {
      if (dropdownRef.current && !dropdownRef.current.contains(e.target)) setShowColumnDropdown(false);
      if (methodDropdownRef.current && !methodDropdownRef.current.contains(e.target)) setShowMethodDropdown(false);
    };
    document.addEventListener("mousedown", closeDropdowns);
    return () => document.removeEventListener("mousedown", closeDropdowns);
  }, []);

  // ✅ Column filtering
  const filteredColumns = columns.filter(col =>
    col.label.toLowerCase().includes(searchTerm.toLowerCase())
  );

  // ✅ Column toggle
  const toggleColumn = (value) => {
    const exists = selectedColumns.some(col => col.value === value);
    if (exists) {
      setSelectedColumns(selectedColumns.filter(col => col.value !== value));
    } else {
      const colToAdd = columns.find(col => col.value === value);
      setSelectedColumns([...selectedColumns, colToAdd]);
    }
  };

  // ✅ Clean data
const handleCleanData = async () => {
  setLoading(true);
  setError(null);

  // ✅ Show tooltip with method description
  setTooltipText(methodDescriptions[cleaningMethod]);
  setShowMethodTooltip(true);
  setTimeout(() => setShowMethodTooltip(false), 60000); // 60 seconds

  try {
    const res = await axios.post(`${API_URL}/api/data_cleaning`, {
      session_id: selectedSession,
      columns: selectedColumns.map(col => col.value),
      method: cleaningMethod,
    });

    const { message } = res.data;

    // ✅ Re-fetch updated data to refresh grid & shape
    await fetchSessionData(selectedSession);

    setCleaningMessage(message || "✅ Data cleaned successfully.");
    setShowToast(true);
    setTimeout(() => setShowToast(false), 10000);

  } catch (err) {
    console.error("❌ Error cleaning data:", err);
    const backendMessage = err.response?.data?.error || "Something went wrong while cleaning the data.";
    setError(backendMessage);
    setCleaningMessage(`❌ ${backendMessage}`);
    setShowToast(true);
    setTimeout(() => setShowToast(false), 10000);
  } finally {
    setLoading(false);
  }
};

  
  
  



  // ✅ Export to CSV
  const handleExportCSV = () => {
      if (gridRef.current) {
        gridRef.current.api.exportDataAsCsv();
      }
    };
  
  // ✅ Export to Excel
  const handleExportExcel = () => {
    if (gridRef.current) {
      gridRef.current.api.exportDataAsExcel();
    }
  };
  



 

  return (
    <div className="missing-data-analysis-container">
      <div className="missing-data-header">🧹 Data Cleaning</div>

      {/* Dataset selection */}
      <div className="dataset-selection-container">
        <div>
          <label>Select Dataset: </label>
          <select
            className="dataset-dropdown"
            onChange={(e) => setSelectedSession(e.target.value)}
            value={selectedSession}
          >
            {sessions.map((s) => (
              <option key={s.id} value={s.id}>{s.name}</option>
            ))}
          </select>
        </div>
        <div className="dataset-shape">{datasetShape}</div>
      </div>

      {/* Column + Method + Button */}
      <div className="column-selection-wrapper">
        <div className="left-section">
          {/* Column dropdown */}
          <div className="column-selection-container">
            <label className="column-label">Select Columns:</label>
            <button
              className="column-dropdown-button"
              onClick={() => setShowColumnDropdown(!showColumnDropdown)}
            >
              Choose Columns ▼
            </button>

            {showColumnDropdown && (
              <div className="column-dropdown" ref={dropdownRef}>
                <button className="close-dropdown" onClick={() => setShowColumnDropdown(false)}>✖</button>
                <input
                  type="text"
                  className="column-search"
                  placeholder="Search columns..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                />
                <label className="column-item">
                  <input
                    type="checkbox"
                    checked={selectedColumns.length === columns.length}
                    onChange={() =>
                      setSelectedColumns(selectedColumns.length === columns.length ? [] : [...columns])
                    }
                  />
                  <strong>Select All</strong>
                </label>
                <div className="column-list">
                  {filteredColumns.map((col) => (
                    <label key={col.value} className="column-item">
                      <input
                        type="checkbox"
                        checked={selectedColumns.some(sel => sel.value === col.value)}
                        onChange={() => toggleColumn(col.value)}
                      />
                      <span className="draggable-handle">☰</span> {col.label}
                    </label>
                  ))}
                </div>
              </div>
            )}
          </div>

          {/* Clean Button */}
          <div className="button-card">
            <button
              className="generate-analysis-btn"
              onClick={handleCleanData}
              disabled={loading}
            >
              {loading 
                ? `🧼 Cleaning with ${cleaningMethods.find(m => m.value === cleaningMethod)?.label || "..."}` 
                : `🧼 Clean (${cleaningMethods.find(m => m.value === cleaningMethod)?.label || "..."})`
              }

            </button>
            {error && <div className="error-message">{error}</div>}
          </div>
        </div>

        {/* Cleaning Method Selector */}
        <div className="method-selection-container">
          <label className="method-label">Data Cleaning Method:</label>
          <div className="method-dropdown">
            <button
              className="method-dropdown-button"
              onClick={() => setShowMethodDropdown(!showMethodDropdown)}
            >
              {cleaningMethods.find(m => m.value === cleaningMethod)?.label || "Select Method"} ▼
            </button>
            {showMethodDropdown && (
              <div className="method-dropdown-list" ref={methodDropdownRef}>
                {cleaningMethods.map((m) => (
                  <label key={m.value} className="method-item">
                    <input
                      type="radio"
                      name="cleaningMethod"
                      value={m.value}
                      checked={cleaningMethod === m.value}
                      onChange={() => {
                        setCleaningMethod(m.value);
                        setShowMethodDropdown(false);
                      }}
                    />
                    {m.label}
                  </label>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>

      <div className="ag-grid-wrapper">
      {/* Floating Export Buttons */}
      <div className="floating-export-buttons">
        <button className="export-btn" onClick={handleExportCSV} title="Export as CSV">📄</button>
        <button className="export-btn" onClick={handleExportExcel} title="Export as Excel">📊</button>
      </div>

      {/* Table */}
      <div className="ag-theme-alpine">
        <AgGridReact
          ref={gridRef}
          columnDefs={columnDefs}
          rowData={rowData}
          pagination={true}
          paginationPageSize={25}
          domLayout="normal"
        />
      </div>
    
    {/* Toast UI Element to display cleaning message */}
      {showToast && (
      <div className="toast-message">
        {cleaningMessage}
      </div>
    )}



    {/* 🧬 Deep Learning Loader or 🔄 General Loader */}
    {loading && (
      <div className={cleaningMethod === "autoencoder" ? "deep-learning-loader" : "general-loader"}>
        {cleaningMethod === "autoencoder" ? (
          <>
            <div className="dna-strand">
              <div className="bar"></div>
              <div className="bar"></div>
              <div className="bar"></div>
              <div className="bar"></div>
              <div className="bar"></div>
            </div>
            <p className="loader-text">Training Neural Network... Please wait 🧠</p>
          </>
        ) : (
          <>
            <div className="spinner"></div>
            <p className="loader-text">Processing your data... Please wait ⏳</p>
          </>
        )}
      </div>
    )}




        {/* Tooltip showing method explanation */}
        {showMethodTooltip && (
      <div className="method-tooltip">
        <span className="tooltip-icon">💡</span>
        <span className="tooltip-text">{tooltipText}</span>
      </div>
    )}


    </div>


    </div>
  );
};

export default DataCleaning;
