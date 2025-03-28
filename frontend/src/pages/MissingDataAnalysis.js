import "./MissingDataAnalysis.css";
import React, { useState, useEffect, useRef } from "react";
import ReactECharts from "echarts-for-react";
import axios from "axios";

const API_URL = "http://127.0.0.1:5050"; // Backend API URL

const MissingDataAnalysis = () => {
    const [sessions, setSessions] = useState([]);
    const [selectedSession, setSelectedSession] = useState(null);
    const [datasetShape, setDatasetShape] = useState("(0, 0)");
    const [columns, setColumns] = useState([]);
    const [selectedColumns, setSelectedColumns] = useState([]);
    const [showColumnDropdown, setShowColumnDropdown] = useState(false);
    const [searchTerm, setSearchTerm] = useState("");
    const dropdownRef = useRef(null);
    const [selectedAnalysis, setSelectedAnalysis] = useState("matrix"); // Default to Missing Data Pattern
    const [showAnalysisDropdown, setShowAnalysisDropdown] = useState(false);
    const methodDropdownRef = useRef(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);
    const [missingMatrixData, setMissingMatrixData] = useState(null); // Store missing matrix data
    const [missingMatrixImage, setMissingMatrixImage] = useState(null); // Store base64 image



    // ✅ Define Analysis Methods (Like Visualization Methods in Distribution Analysis)
    const analysisMethods = [
        { label: "Missing Pattern (Matrix)", value: "matrix" },
        { label: "Missing Data Correlation", value: "correlation" },
        { label: "Missing Data Distribution", value: "distribution" },
        { label: "Hierarchical Clustering", value: "hierarchical" } // ✅ New option added
    ];
    
    
    

    const handleAnalysisSelection = (methodValue) => {
        setSelectedAnalysis(methodValue);
        setShowAnalysisDropdown(false); // Close dropdown after selection
    };

    const toggleAnalysisDropdown = () => {
        setShowAnalysisDropdown(prev => !prev);
    };

    useEffect(() => {
        const handleClickOutside = (event) => {
            if (methodDropdownRef.current && !methodDropdownRef.current.contains(event.target)) {
                setShowAnalysisDropdown(false);
            }
        };

        document.addEventListener("mousedown", handleClickOutside);
        return () => {
            document.removeEventListener("mousedown", handleClickOutside);
        };
    }, []);

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





    

    const fetchMissingDataAnalysis = async () => {
        if (!selectedSession || selectedColumns.length === 0) {
            setError("Please select a dataset and at least one column.");
            return;
        }
    
        setLoading(true);
        setError(null);
    
        try {
            const response = await axios.post(`${API_URL}/api/missing_data_analysis`, {
                session_id: selectedSession,
                columns: selectedColumns.map(col => col.value), // Extract column names
                analysis_type: selectedAnalysis.trim(), // Ensure correct analysis type
            });
    
            console.log("🔹 API Response:", response.data); // Debugging
    
            if (response.data.image_base64) {
                setMissingMatrixImage(`data:image/png;base64,${response.data.image_base64}`); // Convert to image format
            } else {
                setError("No missing data visualization found or incorrect response format.");
            }
    
        } catch (err) {
            console.error("❌ Error fetching missing data analysis:", err);
            setError("Failed to fetch missing data analysis. Please try again.");
        } finally {
            setLoading(false);
        }
    };
    
    



    /* ✅ Function to Save Chart */
    const saveChart = () => {
        const imgElement = document.getElementById("missing-data-img");
        if (!imgElement) return;

        const link = document.createElement("a");
        link.href = imgElement.src;
        link.download = "missing_data_matrix.png";
        link.click();
    };


    

    
    
    
    







    return (
        <div className="missing-data-analysis-container">
            {/* ✅ Header */}
            <div className="missing-data-header">📊 Missing Data Analysis</div>
    
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
                                {/* Close Button */}
                                <button className="close-dropdown" onClick={() => setShowColumnDropdown(false)}>
                                    ✖
                                </button>
    
                                {/* Search Bar */}
                                <input
                                    type="text"
                                    placeholder="Search columns..."
                                    className="column-search"
                                    value={searchTerm}
                                    onChange={(e) => setSearchTerm(e.target.value)}
                                />
    
                                {/* ✅ "Select All" Option */}
                                <label className="column-item">
                                    <input
                                        type="checkbox"
                                        checked={selectedColumns.length === columns.length && columns.length > 0}
                                        onChange={() => {
                                            setSelectedColumns(selectedColumns.length === columns.length ? [] : [...columns]);
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
                                            <span className="draggable-handle">☰</span> {col.label}
                                        </label>
                                    ))}
                                </div>
                            </div>
                        )}
                    </div>
    
                    {/* ✅ Generate Missing Data Analysis Button */}
                    <div className="button-card">
                        <button className="generate-analysis-btn" onClick={fetchMissingDataAnalysis} disabled={loading}>
                            {loading ? `Generating ${selectedAnalysis}...` : `Generate ${selectedAnalysis}`}
                        </button>
                        {error && <div className="error-message">{error}</div>}
                    </div>
                </div>
    
                {/* ✅ Missing Data Analysis Type Selection */}
                <div className="method-selection-container">
                    <label className="method-label">Select Analysis Type:</label>
                    <div className="method-dropdown">
                        <button
                            className={`method-dropdown-button ${showAnalysisDropdown ? "active" : ""}`}
                            onClick={toggleAnalysisDropdown}
                        >
                            {analysisMethods.find((m) => m.value === selectedAnalysis)?.label || "Select Analysis"} ▼
                        </button>
    
                        {showAnalysisDropdown && (
                            <div className="method-dropdown-list" ref={methodDropdownRef}>
                                {analysisMethods.map((method) => (
                                    <label key={method.value} className="method-item">
                                        <input
                                            type="radio"
                                            name="analysisMethod"
                                            value={method.value}
                                            checked={selectedAnalysis === method.value}
                                            onChange={() => handleAnalysisSelection(method.value)}
                                        />
                                        {method.label}
                                    </label>
                                ))}
                            </div>
                        )}
                    </div>
                </div>
            </div>


           {/* ✅ Display Missing Data Visualization Based on Selected Analysis */}
            {missingMatrixImage && (
                <div className="missing-data-visualization-container">
                    <div style={{ position: "relative" }}>
                        <button className="save-chart-btn" onClick={saveChart} title="Save">💾</button>
                    </div>

                    {/* ✅ Chart Title */}
                    <h3 className="missing-data-title">
                    {selectedAnalysis === "matrix" 
                        ? "Missing Data Pattern" 
                        : selectedAnalysis === "correlation" 
                        ? "Missing Data Correlation"
                        : selectedAnalysis === "distribution"
                        ? "Missing Data Distribution"
                        : "Hierarchical Clustering of Missing Data"} {/* ✅ Added for hierarchical clustering */}
                </h3>

                    {/* ✅ Scrollable Container for Large Datasets */}
                    <div className="missing-matrix-scroll-container">
                        <div className="missing-data-chart-container">
                            <img id="missing-data-img" 
                                src={missingMatrixImage} 
                                alt={`Missing Data ${selectedAnalysis}`} 
                                className="missing-data-image" />
                        </div>
                    </div>
                </div>
            )}








        </div>
    );
    };
    export default MissingDataAnalysis;
    
    
    




