import "./CorrelationMatrix.css";
import React, { useState, useEffect } from "react";
import axios from "axios";
import html2canvas from "html2canvas"; // install it: npm install html2canvas

import { useRef } from "react";









const API_URL = "http://127.0.0.1:5050"; // Backend API URL

const CorrelationMatrix = () => {
    const [sessions, setSessions] = useState([]);
    const [selectedSession, setSelectedSession] = useState(null);
    const [datasetShape, setDatasetShape] = useState("(0, 0)");
    const [columns, setColumns] = useState([]);
    
    const [selectedColumns, setSelectedColumns] = useState([]);
    const [correlationData, setCorrelationData] = useState(null);
    const [sortColumn, setSortColumn] = useState(null);
    const [sortOrder, setSortOrder] = useState("asc"); // Default ascending order
    const [showColumnDropdown, setShowColumnDropdown] = useState(false);
    const [searchTerm, setSearchTerm] = useState("");
    const dropdownRef = useRef(null);
    const [selectedMethod, setSelectedMethod] = useState("pearson"); // Default to Pearson

    const [showMethodDropdown, setShowMethodDropdown] = useState(false); // Toggle dropdown visibility
    const methodDropdownRef = useRef(null);
    const [showMethodTooltip, setShowMethodTooltip] = useState(false);
    const [tooltipText, setTooltipText] = useState("");




    const correlationMethods = [
        { label: "Pearson Cor", value: "pearson" },
        { label: "Spearman Cor", value: "spearman" },
        { label: "Kendall Cor", value: "kendall" },
        { label: "Partial Cor", value: "partial" },
        { label: "Distance Cor", value: "distance" },
        { label: "Mutual Information Cor", value: "mutual_information" },
        { label: "Robust Cor", value: "robust" }
    ];


    // Function for correlation methods descriptions 
    const methodDescriptions = {
        pearson: "Measures linear correlation between variables (assumes normality).",
        spearman: "Non-parametric rank-based correlation (monotonic relationships).",
        kendall: "Measures ordinal association between two variables (Kendall Tau).",
        partial: "Computes the correlation between two variables while controlling for the influence of all others using linear regression residuals.",
        distance: "Uses distance correlation (based on Euclidean distances) from `dcor` library to detect both linear and non-linear relationships between variables.",
        mutual_information: "Quantifies how much information one variable provides about another using `mutual_info_regression`.",
        robust: "Applies Winsorization to reduce the influence of extreme values, then computes Spearman correlation for robust results."
    };
    



    const handleMethodSelection = (methodValue) => {
        setSelectedMethod(methodValue);
        setShowMethodDropdown(false);
    
        // ✅ Tooltip behavior
        setTooltipText(methodDescriptions[methodValue]);
        setShowMethodTooltip(true);
        setTimeout(() => setShowMethodTooltip(false), 60000); 
    };
    



    const toggleMethodDropdown = () => {
        setShowMethodDropdown(prev => !prev);
    };



    useEffect(() => {
        const handleClickOutside = (event) => {
            if (methodDropdownRef.current && !methodDropdownRef.current.contains(event.target)) {
                setShowMethodDropdown(false);
            }
        };
    
        document.addEventListener("mousedown", handleClickOutside);
        return () => {
            document.removeEventListener("mousedown", handleClickOutside);
        };
    }, []);
    
    
    
    





    // Function to toggle dropdown visibility
    const toggleDropdown = () => {
        setShowColumnDropdown(prev => !prev);
    };

    // Function to close dropdown if clicking outside
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


    // Function to filter columns based on search input
    const filteredColumns = columns.filter(col => 
        col.label.toLowerCase().includes(searchTerm.toLowerCase())
    );

    // Function to handle column selection
    const handleColumnSelection = (colValue) => {
        const isSelected = selectedColumns.some(col => col.value === colValue);
        if (isSelected) {
            setSelectedColumns(selectedColumns.filter(col => col.value !== colValue));
        } else {
            setSelectedColumns([...selectedColumns, columns.find(col => col.value === colValue)]);
        }
    };
   

    // ✅ Fetch available datasets
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
                        setSelectedSession(sessionEntries[sessionEntries.length - 1].id); // Select last session
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
            if (!selectedSession) return;
        
            try {
                const response = await axios.get(`${API_URL}/api/get_columns/${selectedSession}`);
                if (response.data.columns) {
                    const colOptions = response.data.columns.map(col => ({ label: col, value: col })) || [];
                    setColumns(colOptions); // Ensure columns is never null
                    setSelectedColumns(colOptions.length ? colOptions : []); // Avoid setting null values
                } else {
                    setColumns([]); // Ensure columns always has a default value
                    setSelectedColumns([]);
                }
            } catch (err) {
                console.error("❌ Error fetching columns:", err);
                setColumns([]); // Avoid breaking the table
                setSelectedColumns([]);
            }
        };        

        fetchColumns();
    }, [selectedSession]);

    // ✅ Fetch correlation matrix
    const fetchCorrelationMatrix = async () => {
        if (!selectedSession || selectedColumns.length === 0) return;
    
        // ✅ Show tooltip when heatmap is generated
        setTooltipText(methodDescriptions[selectedMethod]);
        setShowMethodTooltip(true);
        setTimeout(() => setShowMethodTooltip(false), 60000);
    
        try {
            setCorrelationData(null); // ✅ Reset chart before updating data
    
            const response = await axios.post(`${API_URL}/api/correlation_matrix`, {
                session_id: selectedSession,
                columns: selectedColumns.map(col => col.value),
                method: selectedMethod,
            });
    
            const data = response.data.correlation_matrix;
            const labels = Object.keys(data);
    
            let heatmapValues = [];
            labels.forEach((rowLabel) => {
                labels.forEach((colLabel) => {
                    heatmapValues.push({
                        x: colLabel,
                        y: rowLabel,
                        v: data[rowLabel]?.[colLabel] ?? 0,
                    });
                });
            });
    
            let correlationTable = {};
            labels.forEach(row => {
                correlationTable[row] = {};
                labels.forEach(col => {
                    correlationTable[row][col] = data[row]?.[col] ?? 0;
                });
            });
    
            setCorrelationData({
                labels,
                matrix: correlationTable
            });
    
        } catch (err) {
            console.error("❌ Error fetching correlation matrix:", err);
        }
    };
    
    
    
    
    
    
    const getCorrelationColor = (value) => {
        if (value === undefined || value === null) return { background: "#ffffff", text: "#000000" };
    
        // **Define a non-linear scaling to differentiate 1.00 from 0.80 - 0.99**
        let intensity = Math.abs(value);
        
        // Adjusted scaling for better differentiation
        let scaledIntensity;
        if (intensity >= 0.99) {
            scaledIntensity = 255; // Full red/blue
        } else if (intensity >= 0.80) {
            scaledIntensity = 180 + (intensity - 0.80) * (255 - 180); // Transition from light to stronger color
        } else {
            scaledIntensity = Math.floor(255 * intensity); // Normal scaling for lower values
        }
    
        let background;
        if (value > 0) {
            background = `rgb(255, ${255 - scaledIntensity}, ${255 - scaledIntensity})`; // Red for positive
        } else {
            background = `rgb(${255 - scaledIntensity}, ${255 - scaledIntensity}, 255)`; // Blue for negative
        }
    
        // **Ensure text is readable based on background brightness**
        const [r, g, b] = background.match(/\d+/g).map(Number);
        const brightness = (r * 0.299) + (g * 0.587) + (b * 0.114);
        const textColor = brightness > 140 ? "#000000" : "#ffffff"; // Dark text for bright colors, white for dark
    
        return { background, text: textColor };
    };




    // Function to sort the correlation matrix by a selected column
    const handleSort = (column) => {
        if (!correlationData) return;

        const newOrder = sortColumn === column && sortOrder === "asc" ? "desc" : "asc";
        setSortColumn(column);
        setSortOrder(newOrder);

        // Get sorted labels based on column values
        const sortedLabels = [...correlationData.labels].sort((a, b) => {
            const valA = correlationData.matrix[a][column];
            const valB = correlationData.matrix[b][column];

            if (newOrder === "asc") return valA - valB;
            else return valB - valA;
        });

        // Update the state with sorted labels
        setCorrelationData({
            ...correlationData,
            labels: sortedLabels
        });
    };





    // Ensure correlationData exists before sorting
    const sortedLabels = correlationData && correlationData.labels
    ? [...correlationData.labels].sort((a, b) => {
        const valA = correlationData.matrix?.[a]?.[sortColumn] ?? 0;
        const valB = correlationData.matrix?.[b]?.[sortColumn] ?? 0;
        return sortOrder === "asc" ? valA - valB : valB - valA;
    })
    : [];







    // Function to export heatmap as an image
    const exportHeatmapAsImage = () => {
        const heatmapElement = document.querySelector(".heatmap-container");
        if (!heatmapElement) {
            console.error("❌ Heatmap not found!");
            return;
        }

        html2canvas(heatmapElement).then(canvas => {
            const link = document.createElement("a");
            link.download = "correlation_heatmap.png";
            link.href = canvas.toDataURL("image/png");
            link.click();
        });
    };

    // Function to export correlation matrix as CSV
    const exportAsCSV = () => {
        if (!correlationData) return;

        let csvContent = "data:text/csv;charset=utf-8,";

        // Add headers
        csvContent += "COLUMN," + sortedLabels.join(",") + "\n";

        // Add rows
        sortedLabels.forEach(row => {
            let rowValues = sortedLabels.map(col => correlationData.matrix[row][col].toFixed(2));
            csvContent += row + "," + rowValues.join(",") + "\n";
        });

        // Trigger download
        const encodedUri = encodeURI(csvContent);
        const link = document.createElement("a");
        link.setAttribute("href", encodedUri);
        link.setAttribute("download", "correlation_matrix.csv");
        document.body.appendChild(link);
        link.click();
    };





    




    

        return (
            <div className="correlation-matrix-container">
                {/* ✅ Header with Background */}
                <div className="correlation-header">
                    📊 Correlation Matrix
                </div>
        
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
                                <option key={session.id} value={session.id}>{session.name}</option>
                            ))}
                        </select>
                    </div>
        
                    {/* ✅ Dataset Shape */}
                    <div className="dataset-shape">
                        {datasetShape}
                    </div>
                </div>
        
                {/* ✅ Column Selection & Generate Heatmap */}
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
                                    {/* Close Button (X) */}
                                    <button className="close-dropdown" onClick={() => setShowColumnDropdown(false)}>✖</button>

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
                                                    checked={selectedColumns.some(selected => selected.value === col.value)}
                                                    onChange={() => handleColumnSelection(col.value)}
                                                />
                                                <span className="draggable-handle">☰</span> {col.label}
                                            </label>
                                        ))}
                                    </div>
                                </div>
                            )}
                        </div>

                        {/* Generate Heatmap Button */}
                        <div className="button-card">
                            <button className="fetch-button" onClick={fetchCorrelationMatrix}>
                                🚀 Generate Heatmap
                            </button>
                        </div>
                    </div>

                    {/* ✅ Correlation Method Selection - NEW */}
                    <div className="method-selection-container">
                        <label className="method-label">Select Method:</label>
                        <div className="method-dropdown">
                            <button 
                                className={`method-dropdown-button ${showMethodDropdown ? "active" : ""}`}
                                onClick={toggleMethodDropdown}
                            >
                                {correlationMethods.find(m => m.value === selectedMethod)?.label || "Select Method"} ▼
                            </button>

                            {showMethodDropdown && (
                                <div className="method-dropdown-list" ref={methodDropdownRef}>
                                    {correlationMethods.map((method) => (
                                        <label key={method.value} className="method-item">
                                            <input
                                                type="radio"
                                                name="correlationMethod"
                                                value={method.value}
                                                checked={selectedMethod === method.value}
                                                onChange={() => handleMethodSelection(method.value)}
                                            />
                                            {method.label}
                                        </label>
                                    ))}
                                </div>
                            )}
                        </div>
                    </div>

                    {/* Export Buttons at the Far Right */}
                    <div className="export-buttons">
                        <button className="export-button" onClick={exportHeatmapAsImage}>
                            📷 Export as Image
                        </button>
                        <button className="export-button" onClick={exportAsCSV}>
                            📄 Export as CSV
                        </button>
                    </div>
                </div>





        
                {/* ✅ Heatmap Display */}
                {correlationData && (
                    <div className="heatmap-container">
                        <table className="correlation-table">
                        <thead>
                            <tr>
                                <th className="column-header">Column</th> {/* Label for row headers */}
                                {sortedLabels.map((col) => (
                                    <th 
                                        key={col} 
                                        onClick={() => handleSort(col)} 
                                        className={`sortable-header ${sortColumn === col ? 'sorted' : ''}`}
                                    >
                                        {col} {sortColumn === col ? (sortOrder === "asc" ? "🔼" : "🔽") : ""}
                                    </th>
                                ))}
                            </tr>
                        </thead>


                            <tbody>
                                {sortedLabels.map(row => (
                                    <tr key={row}>
                                        <td><strong>{row}</strong></td> {/* Row header */}
                                        {sortedLabels.map(col => (
                                            <td 
                                                key={col}
                                                style={{
                                                    backgroundColor: getCorrelationColor(correlationData.matrix?.[row]?.[col]).background,
                                                    color: getCorrelationColor(correlationData.matrix?.[row]?.[col]).text,
                                                    padding: "8px",
                                                    textAlign: "center",
                                                    fontWeight: "bold",
                                                    cursor: "pointer"
                                                }}
                                            >
                                                {correlationData.matrix?.[row]?.[col]?.toFixed(2) || "0.00"}
                                            </td>
                                        ))}
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                )}


                {showMethodTooltip && (
                <div className="method-tooltip">
                    <span className="tooltip-icon">💡</span>
                    <span className="tooltip-text">{tooltipText}</span>
                </div>
                )}

            </div>
        );            
};

export default CorrelationMatrix;
