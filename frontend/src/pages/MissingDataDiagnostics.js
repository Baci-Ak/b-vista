import "./MissingDataDiagnostics.css";
import React, { useState, useEffect, useRef } from "react";
import axios from "axios";

const API_URL = "http://127.0.0.1:5050"; // Backend API URL

const MissingDataDiagnostics = () => {
    const [sessions, setSessions] = useState([]);
    const [selectedSession, setSelectedSession] = useState(null);
    const [datasetShape, setDatasetShape] = useState("(0, 0)");
    const [columns, setColumns] = useState([]);
    const [selectedColumns, setSelectedColumns] = useState([]);
    const [showColumnDropdown, setShowColumnDropdown] = useState(false);
    const [searchTerm, setSearchTerm] = useState("");
    const dropdownRef = useRef(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);
    const [missingDataResults, setMissingDataResults] = useState(null);

    // ✅ Function to toggle column dropdown visibility
    const toggleDropdown = () => {
        setShowColumnDropdown(prev => !prev);
    };

    // ✅ Function to close column dropdown if clicking outside
    useEffect(() => {
        const handleClickOutside = (event) => {
            if (dropdownRef.current && !dropdownRef.current.contains(event.target)) {
                setShowColumnDropdown(false);
            }
        };

        document.addEventListener("mousedown", handleClickOutside);
        return () => {
            document.removeEventListener("mousedown", handleClickOutside);
        };
    }, []);

    // ✅ Filter Columns Based on Search Input
    const filteredColumns = columns.filter(col => 
        col.label.toLowerCase().includes(searchTerm.toLowerCase())
    );

    // ✅ Handle Column Selection
    const handleColumnSelection = (colValue) => {
        const isSelected = selectedColumns.some(col => col.value === colValue);
        if (isSelected) {
            setSelectedColumns(selectedColumns.filter(col => col.value !== colValue));
        } else {
            setSelectedColumns([...selectedColumns, columns.find(col => col.value === colValue)]);
        }
    };

    // ✅ Fetch available dataset sessions
    useEffect(() => {
        const fetchSessions = async () => {
            try {
                const response = await axios.get(`${API_URL}/api/get_sessions`);
                if (response.data.sessions) {
                    const sessionEntries = Object.entries(response.data.sessions).map(([id, session]) => ({
                        id,
                        name: session.name || `Dataset ${id}`,
                    }));
                    setSessions(sessionEntries);
                    if (sessionEntries.length > 0 && !selectedSession) {
                        setSelectedSession(sessionEntries[sessionEntries.length - 1].id);
                    }
                }
            } catch (err) {
                console.error("❌ Error fetching sessions:", err);
            }
        };

        fetchSessions();
    }, [selectedSession]);

    // ✅ Fetch dataset shape when session is selected
    useEffect(() => {
        if (!selectedSession) return;
    
        const fetchShape = async () => {
            try {
                const response = await axios.get(`${API_URL}/api/session/${selectedSession}`);
                if (response.data.total_rows && response.data.total_columns) {
                    setDatasetShape(`(${response.data.total_rows}, ${response.data.total_columns})`);
                }
            } catch (err) {
                console.error("❌ Error fetching dataset shape:", err);
            }
        };
    
        fetchShape();
    }, [selectedSession]);
    
    // ✅ Fetch column names when session is selected
    useEffect(() => {
        if (!selectedSession) return;
    
        const fetchColumns = async () => {
            try {
                const response = await axios.get(`${API_URL}/api/get_columns/${selectedSession}`);
                if (response.data.columns) {
                    const colOptions = response.data.columns.map(col => ({ label: col, value: col })) || [];
                    setColumns(colOptions);
                    setSelectedColumns(colOptions.length ? colOptions : []);
                } else {
                    setColumns([]);
                    setSelectedColumns([]);
                }
            } catch (err) {
                console.error("❌ Error fetching columns:", err);
                setColumns([]);
                setSelectedColumns([]);
            }
        };
    
        fetchColumns();
    }, [selectedSession]);

    // ✅ Fetch Missing Data Type Analysis
    const fetchMissingDataTypes = async () => {
        if (!selectedSession || selectedColumns.length === 0) {
            setError("Please select a dataset and at least one column.");
            return;
        }

        setLoading(true);
        setError(null);

        try {
            const response = await axios.post(`${API_URL}/api/missing_data_types`, {
                session_id: selectedSession,
                columns: selectedColumns.map(col => col.value), // Extract column names
            });

            console.log("🔹 API Response:", response.data); // Debugging

            if (response.data.results) {
                setMissingDataResults(response.data.results);
            } else {
                setError("No missing data results found.");
            }
        } catch (err) {
            console.error("❌ Error fetching missing data types:", err);
            setError("Failed to fetch missing data types. Please try again.");
        } finally {
            setLoading(false);
        }
    };




    const saveTableAsImage = () => {
        const table = document.querySelector(".missing-data-table");
        if (!table) return;
    
        import("html2canvas").then((html2canvas) => {
            html2canvas.default(table).then((canvas) => {
                const link = document.createElement("a");
                link.download = "missing_data_table.png";
                link.href = canvas.toDataURL();
                link.click();
            });
        });
    };
    


    return (
        <div className="missing-data-analysis-container">
            {/* ✅ Header */}
            <div className="missing-data-header">📊 Types of Missing Data</div>

            {/* ✅ Dataset Selection & Shape Display */}
            <div className="dataset-selection-container">
                <div>
                    <label>Select Dataset: </label>
                    <select
                        className="dataset-dropdown"
                        onChange={(e) => setSelectedSession(e.target.value)}
                        value={selectedSession}
                    >
                        {sessions.map((session) => (
                            <option key={session.id} value={session.id}>
                                {session.name}
                            </option>
                        ))}
                    </select>
                </div>

                {/* ✅ Dataset Shape */}
                <div className="dataset-shape">{datasetShape}</div>
            </div>

            {/* ✅ Column Selection & Generate Analysis */}
            <div className="column-selection-wrapper">
                <div className="left-section">
                    {/* Select Columns Button */}
                    <div className="column-selection-container">
                        <label className="column-label">Select Columns:</label>
                        <button
                            className={`column-dropdown-button ${showColumnDropdown ? "active" : ""}`}
                            onClick={toggleDropdown}
                        >
                            Choose Columns ▼
                        </button>

                        {showColumnDropdown && (
                            <div className="column-dropdown" ref={dropdownRef}>
                                {/* Search Bar */}
                                <input
                                    type="text"
                                    placeholder="Search columns..."
                                    className="column-search"
                                    value={searchTerm}
                                    onChange={(e) => setSearchTerm(e.target.value)}
                                />

                                {/* ✅ "Select All" Option */}
                                <label className="column-item select-all">
                                    <input
                                        type="checkbox"
                                        checked={selectedColumns.length === columns.length && columns.length > 0}
                                        onChange={() => {
                                            setSelectedColumns(
                                                selectedColumns.length === columns.length ? [] : [...columns]
                                            );
                                        }}
                                    />
                                    <strong>Select All</strong>
                                </label>

                                {/* Column List */}
                                <div className="column-list">
                                    {filteredColumns.map((col) => (
                                        <label key={col.value} className="column-item">
                                            <input
                                                type="checkbox"
                                                checked={selectedColumns.some((selected) => selected.value === col.value)}
                                                onChange={() => handleColumnSelection(col.value)}
                                            />
                                            {col.label}
                                        </label>
                                    ))}
                                </div>
                            </div>
                        )}
                    </div>

                    {/* ✅ Generate Missing Data Type Analysis Button */}
                    <button className="generate-analysis-btn" onClick={fetchMissingDataTypes} disabled={loading}>
                        {loading ? "Analyzing..." : "Generate Missing Data Type"}
                    </button>

                    {error && <div className="error-message">{error}</div>}
                </div>
            </div>

            
            {/* ✅ Render Results Table */}
{missingDataResults && (
    <div className="missing-data-results">
        <h3 className="missing-data-title">Missing Data Diagnostics</h3>

        {/* ✅ Table Container for Relative Positioning */}
        <div className="table-container">
            {/* ✅ Save Button (Top-Right) */}
            <button className="save-chart-btn" onClick={saveTableAsImage} title="Save Table">
                💾
            </button>

            <table className="missing-data-table">
                <thead>
                    <tr>
                        <th>Test</th>
                        <th>Test Statistic</th>
                        <th>Degrees of Freedom (df)</th>
                        <th>p-value</th>
                        <th>Decision Rule</th>
                    </tr>
                </thead>
                <tbody>
                    {["MCAR_Test", "MAR_Test", "NMAR_Test"].map((testKey) => {
                        const testResult = missingDataResults?.[testKey] || {};
                        const decision = testResult.decision || "N/A";

                        return (
                            <tr key={testKey}>
                                <td>{testResult.test || "N/A"}</td>
                                <td>{testResult.statistic !== undefined ? testResult.statistic : "N/A"}</td>
                                <td>{testResult.df !== undefined ? testResult.df : "N/A"}</td>
                                <td>{testResult.p_value !== undefined ? testResult.p_value : "N/A"}</td>
                                <td className={
                                    testResult.error ? "error" :
                                    testResult.warning ? "warning" :
                                    decision.includes("NMAR") ? "nmar" :
                                    decision.includes("MAR") ? "mar" :
                                    decision.includes("MCAR") ? "mcar" :
                                    "neutral"
                                }>
                                    {testResult.error || testResult.warning || decision}
                                </td>
                            </tr>
                        );
                    })}
                </tbody>
            </table>
        </div>
    </div>
)}






        </div>
    );
};

export default MissingDataDiagnostics;
