import "./DistributionAnalysis.css";
import React, { useState, useEffect } from "react";
import axios from "axios";
import html2canvas from "html2canvas"; // install it: npm install html2canvas
import Plot from "react-plotly.js";
import ReactECharts from "echarts-for-react";
import * as echarts from "echarts";



import { useRef } from "react";









const API_URL = "http://127.0.0.1:5050"; // Backend API URL

const DistributionAnalysis = () => {
    const [sessions, setSessions] = useState([]);
    const [selectedSession, setSelectedSession] = useState(null);
    const [datasetShape, setDatasetShape] = useState("(0, 0)");
    const [columns, setColumns] = useState([]);
    const [selectedColumns, setSelectedColumns] = useState([]);
    const [sortColumn, setSortColumn] = useState(null);
    const [sortOrder, setSortOrder] = useState("asc"); // Default ascending order
    const [showColumnDropdown, setShowColumnDropdown] = useState(false);
    const [searchTerm, setSearchTerm] = useState("");
    const dropdownRef = useRef(null);
    const [selectedVisualization, setSelectedVisualization] = useState("histogram");
    
    const [showVisualizationDropdown, setShowVisualizationDropdown] = useState(false);
 // Toggle dropdown visibility
    const methodDropdownRef = useRef(null);
    const [histogramImage, setHistogramImage] = useState(null); // Store received histogram image
    const [loading, setLoading] = useState(false); // Loading state
    const [error, setError] = useState(null); // Store any API errors
    const [histogramData, setHistogramData] = useState(null); // Store histogram data
    const [boxPlotData, setBoxPlotData] = useState(null); // Store box plot data
    const [rotatePlot, setRotatePlot] = useState(false); // Controls plot rotation
    const [showOutliers, setShowOutliers] = useState(true); // Controls outlier visibility
    const echartsRef = useRef(null); // Reference to ECharts instance
    const [showStatsLabels, setShowStatsLabels] = useState(false);
    const [showQQPlotStats, setShowQQPlotStats] = useState({});


    // ✅ Helper function to safely format numbers
    const safeFormat = (value, decimals = 3) => {
        return value !== undefined && value !== null ? value.toFixed(decimals) : "N/A";
    };









    const visualizationMethods = [
        { label: "Histogram", value: "histogram" },    
        { label: "Box Plot", value: "boxplot" },
        { label: "QQ-Plot", value: "qqplot" },

    ];
    



    const handleVisualizationSelection = (methodValue) => {
        setSelectedVisualization(methodValue);
        setShowVisualizationDropdown(false); // Close dropdown after selection
    };
    



    const toggleVisualizationDropdown = () => {
        setShowVisualizationDropdown(prev => !prev);
    };
    



    useEffect(() => {
        const handleClickOutside = (event) => {
            if (methodDropdownRef.current && !methodDropdownRef.current.contains(event.target)) {
                setShowVisualizationDropdown(false);
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




    

    const [qqPlotData, setQQPlotData] = useState(null); // Store QQ-Plot data

    const fetchDistributionPlot = async () => {
        if (!selectedSession || selectedColumns.length === 0) {
            setError("Please select a dataset and at least one column.");
            return;
        }

        setLoading(true);
        setError(null);

        try {
            const response = await axios.post(`${API_URL}/api/distribution_analysis`, {
                session_id: selectedSession,
                columns: selectedColumns.map(col => col.value), // Extract column names
                plot_type: selectedVisualization, // Dynamically choose the plot type
                show_kde: selectedVisualization === "histogram", // Only show KDE for histogram
            });

            if (selectedVisualization === "histogram" && response.data.histograms) {
                setHistogramData(response.data.histograms);
                setBoxPlotData(null);
                setQQPlotData(null); // Clear QQ-Plot data
            } else if (selectedVisualization === "boxplot" && response.data.box_plots) {
                setBoxPlotData(response.data.box_plots);
                setHistogramData(null);
                setQQPlotData(null); // Clear QQ-Plot data
            } else if (selectedVisualization === "qqplot" && response.data.qq_plots) {
                setQQPlotData(response.data.qq_plots);
                setHistogramData(null);
                setBoxPlotData(null); // Clear histogram & box plot data
            } else {
                setError("No valid dataframe received.");
            }
        } catch (err) {
            console.error("Error fetching distribution plot:", err);
            setError("Failed to fetch distribution plot.");
        } finally {
            setLoading(false);
        }
    };




    const downloadStatsAsCSV = (col, data) => {
        let csvContent = `Metric,Value\n`;
    
        // Helper function to safely format numbers
        const safeFormat = (value, decimals = 3) => {
            return value !== undefined && value !== null ? value.toFixed(decimals) : "N/A";
        };
    
        // ✅ Add normality metrics with safe checks
        csvContent += `Mean,${safeFormat(data.mean, 2)}\n`;
        csvContent += `Median,${safeFormat(data.median, 2)}\n`;
        csvContent += `Standard Deviation,${safeFormat(data.std_dev)}\n`;
        csvContent += `Variance,${safeFormat(data.variance)}\n`;
        csvContent += `Skewness,${safeFormat(data.skewness)}\n`;
        csvContent += `Kurtosis,${safeFormat(data.kurtosis)}\n`;
        csvContent += `R² (Goodness of Fit),${safeFormat(data.r_squared)}\n`;
        csvContent += `Slope,${safeFormat(data.slope)}\n`;
        csvContent += `Intercept,${safeFormat(data.intercept)}\n`;
        csvContent += `Residual Std Error (RSE),${safeFormat(data.residual_std_error)}\n`;
    
        // ✅ Add normality test results with safe checks
        csvContent += `\nNormality Tests,Statistic,p-Value\n`;
        Object.entries(data.normality_tests || {}).forEach(([test, results]) => {
            csvContent += `${test},${safeFormat(results.statistic)},${results.p_value ? results.p_value.toExponential(2) : "N/A"}\n`;
        });
    
        // ✅ Add Anderson-Darling Critical Values (if present)
        if (data.normality_tests && data.normality_tests["Anderson-Darling"]) {
            csvContent += `\nAnderson-Darling Critical Values\nSignificance Level (%),Critical Value\n`;
            data.normality_tests["Anderson-Darling"].critical_values.forEach((value, index) => {
                csvContent += `${data.normality_tests["Anderson-Darling"].significance_levels[index]}%,${safeFormat(value)}\n`;
            });
        }
    
        // ✅ Create and trigger the CSV file download
        const blob = new Blob([csvContent], { type: "text/csv" });
        const link = document.createElement("a");
        link.href = URL.createObjectURL(blob);
        link.download = `${col}_normality_stats.csv`;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
    };












    


    

    

    



    

    return (
        <div className="distribution-analysis-container">
            {/* ✅ Header */}
            <div className="distribution-header">📊 Distribution Analysis</div>
    
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
    
            {/* ✅ Column Selection & Histogram Generation */}
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
    
                    {/* ✅ Generate Histogram Button */}
                    <div className="button-card">
                    <button className="generate-histogram-btn" onClick={fetchDistributionPlot} disabled={loading}>
                        {loading ? `Generating ${selectedVisualization}...` : `Generate ${selectedVisualization}`}
                    </button>
                        {error && <div className="error-message">{error}</div>}
                    </div>
                </div>
    
                {/* ✅ Visualization Method Selection */}
                <div className="method-selection-container">
                    <label className="method-label">Select Visualization:</label>
                    <div className="method-dropdown">
                        <button
                            className={`method-dropdown-button ${showVisualizationDropdown ? "active" : ""}`}
                            onClick={toggleVisualizationDropdown}
                        >
                            {visualizationMethods.find((m) => m.value === selectedVisualization)?.label || "Select Visualization"} ▼
                        </button>
    
                        {showVisualizationDropdown && (
                            <div className="method-dropdown-list" ref={methodDropdownRef}>
                                {visualizationMethods.map((method) => (
                                    <label key={method.value} className="method-item">
                                        <input
                                            type="radio"
                                            name="visualizationMethod"
                                            value={method.value}
                                            checked={selectedVisualization === method.value}
                                            onChange={() => handleVisualizationSelection(method.value)}
                                        />
                                        {method.label}
                                    </label>
                                ))}
                            </div>
                        )}
                    </div>
                </div>
            </div>
    
            {/* ✅ Scrollable Histogram Grid */}
            {selectedVisualization === "histogram" && histogramData && Object.keys(histogramData).length > 0 && (
                <div className="histogram-scroll-container">
                    <div className="histogram-grid">
                        {Object.entries(histogramData).map(([col, data], index) => (
                            <div className="histogram-box" key={col}>
                                {/* ✅ Title should be part of the same box as the chart */}
                                <div className="histogram-header">
                                    <h4 
                                        className="histogram-title" 
                                        data-full-title={`${col} Distribution`}
                                        title={`${col} Distribution`} /* Fallback tooltip */
                                    >
                                        {col.length > 52 ? col.slice(0, 52) + "..." : col} Distribution
                                    </h4>
                                </div>

                                <div className="histogram-chart-container">
                                    <Plot
                                        data={[
                                            // Handle Single-Value Columns
                                            data.bins.length === 2 && data.frequencies.length === 1
                                                ? {
                                                    x: data.bins,
                                                    y: [data.frequencies[0], data.frequencies[0]],
                                                    type: "bar",
                                                    name: `${col}`,
                                                    marker: { color: "blue" },
                                                    hoverinfo: "skip",
                                                    hovertemplate: `<b>${col}</b><br>%{x}<br>Freq: %{y}<extra></extra>`
                                                }
                                                : {
                                                    x: data.bins,
                                                    y: data.frequencies,
                                                    type: "bar",
                                                    name: `${col}`,
                                                    marker: { color: ["blue", "grey", "green", "purple", "red", "orange", "lemon", "darkblue", "brown"][index % 9] },
                                                    hoverinfo: "skip",
                                                    hovertemplate: `<b>${col.length > 20 ? col.slice(0, 20) + "..." : col}</b><br>%{x}<br>Freq: %{y}<extra></extra>`
                                                },
                                            // KDE Curve
                                            data.kde_x.length > 0 && data.kde_y.length > 0
                                                ? {
                                                    x: data.kde_x,
                                                    y: data.kde_y,
                                                    type: "scatter",
                                                    mode: "lines",
                                                    name: "KDE",
                                                    line: {
                                                        color: ["#FF5733", "#33FF57", "#3357FF", "#FF33A8", "#33FFF2"][index % 5],
                                                        width: 2.5,
                                                        shape: "spline",
                                                    },
                                                    hoverinfo: "skip",
                                                    hovertemplate: `<b>KDE(Density): </b>%{y}</b><extra></extra>`,
                                                    yaxis: "y2",
                                                }
                                                : null,
                                            // Median Line (Dotted Vertical Line)
                                            {
                                                x: [data.median, data.median],
                                                y: [0, Math.max(...data.frequencies) * 1.1],
                                                type: "scatter",
                                                mode: "lines",
                                                name: "Median",
                                                line: {
                                                    color: ["#E91E63", "#9C27B0", "#673AB7", "#3F51B5", "#009688"][index % 5],
                                                    width: 2.5,
                                                    dash: "dot",
                                                },
                                                hoverinfo: "x",
                                                hovertemplate: `<b>Median: </b>%{x}</b><extra></extra>`
                                            },
                                            // Mean Line (Dashed Vertical Line)
                                            {
                                                x: [data.mean, data.mean],
                                                y: [0, Math.max(...data.frequencies) * 1.1],
                                                type: "scatter",
                                                mode: "lines",
                                                name: "Mean",
                                                line: {
                                                    color: ["#FFA500", "#FFC107", "#FF9800", "#FF5722", "#FF4500"][index % 5],
                                                    width: 2.5,
                                                    dash: "dash",
                                                },
                                                hoverinfo: "x",
                                                hovertemplate: `<b>Mean: </b>%{x}</b><extra></extra>`
                                            },
                                        ].filter(Boolean)}
                                        layout={{
                                            xaxis: { title: col },
                                            yaxis: { title: "Frequency" },
                                            yaxis2: {
                                                title: "KDE",
                                                overlaying: "y",
                                                side: "right",
                                                showgrid: false,
                                            },
                                            legend: {
                                                x: 0.5,
                                                y: 1.15,
                                                xanchor: "center",
                                                yanchor: "bottom",
                                                orientation: "h",
                                            },
                                            hovermode: "x unified",
                                            barmode: "overlay",
                                            bargap: 0.1,
                                            autosize: false,
                                            width: 500,
                                            height: 400,
                                            margin: { l: 60, r: 60, t: 100, b: 60 },
                                        }}
                                        config={{
                                            responsive: true,
                                            displayModeBar: true,
                                            displaylogo: false,
                                            scrollZoom: true,
                                            modeBarButtonsToRemove: ["sendDataToCloud"],
                                        }}
                                    />
                                </div>
                            </div>
                        ))}
                    </div>
                </div>
            )}

                {/* Box Plot Section (Now optimized without a legend) */}
                {selectedVisualization === "boxplot" && boxPlotData && Object.keys(boxPlotData).length > 0 && (
                    <div className="boxplot-scroll-container">
                        <div className="boxplot-grid">
                            {Object.entries(boxPlotData).map(([col, data], index) => {
                                // Dynamic color selection (same logic as histogram)
                                const colors = ["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd", "#8c564b", "#e377c2", "#7f7f7f", "#bcbd22"];
                                const boxColor = colors[index % colors.length]; // Assign unique color to each box
                                const medianColor = ["#DFFF00", "#66ccff", "#1f77b4", "#ff7f0e", "#33FF57", "#3357FF", "#FF33A8", "#33FFF2"][index % 8]; // Distinct median line color

                                return (
                                    <div className="boxplot-box" key={col}>
                                        {/* ✅ Title & Log-Transform Warning */}
                                        <div className="boxplot-header">
                                            <h4 className="boxplot-title" data-full-title={`${col} Box Plot`} title={`${col} Box Plot`}>
                                                {col.length > 52 ? col.slice(0, 52) + "..." : col} Box Plot
                                            </h4>

                                            {/* ✅ Log-Transform Warning (Shows Actual Skewness Value) */}
                                            {data.log_transformed && data.skewness !== undefined && (
                                                <div className="log-warning">
                                                    ⚠️ Log-transformed due to high skewness ({data.skewness.toFixed(2)} &gt; 2).
                                                </div>
                                            )}

                                        </div>

                                        {/* ✅ Box Plot Chart (No legend) */}
                                        <div className="boxplot-chart-container">
                                            <ReactECharts
                                                option={{
                                                    tooltip: {
                                                        trigger: "item",
                                                        formatter: function (params) {
                                                            let columnName = params.name;
                                                            const data = boxPlotData[columnName];

                                                            if (!data) return "";

                                                            // ✅ Truncate long column names for better display
                                                            const maxLength = 21;
                                                            let truncatedColumnName = columnName.length > maxLength 
                                                                ? columnName.substring(0, maxLength) + "..." 
                                                                : columnName;

                                                            // ✅ Format numbers for readability (Adds commas & limits decimals)
                                                            const formatNumber = (num) => {
                                                                return num !== undefined && num !== null
                                                                    ? num.toLocaleString(undefined, { maximumFractionDigits: 3 }) 
                                                                    : "N/A";
                                                            };

                                                            

                                                            // ✅ Handle Box Plot Hover
                                                            if (params.seriesType === "boxplot") {
                                                                return `<b>${truncatedColumnName} Box Plot</b><br>
                                                                        Min: ${formatNumber(data.min)}<br>
                                                                        Q1: ${formatNumber(data.q1)}<br>
                                                                        Median: ${formatNumber(data.median)}<br>
                                                                        Q3: ${formatNumber(data.q3)}<br>
                                                                        Max: ${formatNumber(data.max)}
                                                                        `;
                                                            }

                                                            // ✅ Handle Scatter (Outliers) Hover
                                                            if (params.seriesType === "scatter") {
                                                                return `<b>Outlier</b>: ${formatNumber(params.data[1])}`;
                                                            }

                                                            return "";
                                                        },
                                                    },
                                                    toolbox: {
                                                        show: true,
                                                        feature: {
                                                            saveAsImage: { show: true, title: "Save", filename: "boxplot", pixelRatio: 2 },
                                                            restore: { show: true, title: "Reset View" },
                                                            dataView: { 
                                                                show: true, 
                                                                title: "View Data",
                                                                readOnly: true, 
                                                                lang: ["Box Plot Data", "Close", "Refresh"],
                                                                optionToContent: function(opt) {
                                                                    const series = opt.series[0];
                                                                    const table = document.createElement("table");
                                                                    table.style.borderCollapse = "collapse";
                                                                    table.style.width = "100%";
                                                                    table.style.textAlign = "center";

                                                                    let headerRow = "<tr style='font-weight: bold; background: #f5f5f5;'>";
                                                                    ["Column", "Min", "Q1", "Median", "Q3", "Max"].forEach(header => {
                                                                        headerRow += `<th style='border: 1px solid #ccc; padding: 5px;'>${header}</th>`;
                                                                    });
                                                                    headerRow += "</tr>";

                                                                    let rows = "";
                                                                    series.data.forEach((data, index) => {
                                                                        rows += "<tr>";
                                                                        rows += `<td style='border: 1px solid #ccc; padding: 5px;'>${opt.xAxis[0].data[index]}</td>`;
                                                                        data.forEach(value => {
                                                                            rows += `<td style='border: 1px solid #ccc; padding: 5px;'>${value}</td>`;
                                                                        });
                                                                        rows += "</tr>";
                                                                    });

                                                                    table.innerHTML = `<thead>${headerRow}</thead><tbody>${rows}</tbody>`;

                                                                    // ✅ Add Download CSV Button
                                                                    const downloadBtn = document.createElement("button");
                                                                    downloadBtn.innerText = "Download CSV";
                                                                    downloadBtn.style.marginTop = "10px";
                                                                    downloadBtn.onclick = function() {
                                                                        let csvContent = "Column,Min,Q1,Median,Q3,Max\n";
                                                                        opt.xAxis[0].data.forEach((colName, index) => {
                                                                            csvContent += `${colName},${series.data[index].join(",")}\n`;
                                                                        });
                                                                        const blob = new Blob([csvContent], { type: "text/csv" });
                                                                        const link = document.createElement("a");
                                                                        link.href = URL.createObjectURL(blob);
                                                                        link.download = "boxplot_data.csv";
                                                                        document.body.appendChild(link);
                                                                        link.click();
                                                                        document.body.removeChild(link);
                                                                    };

                                                                    const container = document.createElement("div");
                                                                    container.appendChild(table);
                                                                    container.appendChild(downloadBtn);

                                                                    return container;
                                                                }
                                                            }
                                                        },
                                                        right: "5%", // Align to the right
                                                        top: "5%", // Align to the top
                                                    },
                                                    xAxis: {
                                                        type: "category",
                                                        data: [col],
                                                        axisLabel: { rotate: 45, overflow: "truncate", fontSize: 12, interval: 0, fontWeight: "bold"},
                                                    },
                                                    yAxis: {
                                                        type: "value",
                                                        name: "Values",
                                                    },
                                                    series: [
                                                        {
                                                            name: "Box Plot",
                                                            type: "boxplot",
                                                            data: [[data.min, data.q1, data.median, data.q3, data.max]],
                                                            itemStyle: { color: boxColor },
                                                        },
                                                        {
                                                            name: "Median",
                                                            type: "scatter",
                                                            data: [[col, data.median]],
                                                            symbol: "diamond",
                                                            symbolSize: 10,
                                                            itemStyle: { color: medianColor },
                                                        },
                                                        {
                                                            name: "Outliers",
                                                            type: "scatter",
                                                            data: data.outliers.map((value) => [col, value]),
                                                            symbolSize: 10,
                                                            itemStyle: { color: "red" },
                                                        },
                                                    ],
                                                    legend: {
                                                        show: true,
                                                        data: [
                                                            { name: "Box Plot", itemStyle: { color: boxColor } }, 
                                                            { name: "Median", itemStyle: { color: medianColor } }, 
                                                            { name: "Outliers", itemStyle: { color: "red" } }
                                                        ],
                                                        textStyle: {
                                                            fontSize: 12,
                                                            color: "#333",
                                                        },
                                                        selectedMode: "multiple",
                                                    },
                                                }}
                                                style={{ width: "500px", height: "400px" }}
                                            />
                                        </div>
                                    </div>
                                );
                            })}
                        </div>
                    </div>
                )}








                    {/* ✅ Scrollable QQ-Plot Grid */}
{selectedVisualization === "qqplot" && qqPlotData && Object.keys(qqPlotData).length > 0 && (
    <div className="qqplot-scroll-container">
        <div className="qqplot-grid">
            {Object.entries(qqPlotData).map(([col, data], index) => {
                if (!data) return null; // ✅ Ensure data exists before proceeding

                // ✅ Dynamic Color Selection
                const colors = ["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd", "#8c564b", "#e377c2", "#7f7f7f", "#bcbd22"];
                const sampleColor = colors[index % colors.length]; // Unique per column
                const normalityColor = ["blue", "grey", "#e377c2", "green", "purple", "red", "orange", "lemon", "darkblue", "brown"][index % 9]; // Red for normality line
                const olsColor = ["#FF5733", "#1f77b4", "#ff7f0e", "#33FF57", "#3357FF", "#FF33A8", "#33FFF2", ][index % 7]; // Green for OLS fit line

                // ✅ Compute Min/Max Range (Prevent Undefined Errors)
                const xMin = Math.min(...data.theoretical_quantiles);
                const xMax = Math.max(...data.theoretical_quantiles);
                const yMin = Math.min(...data.sample_quantiles);
                const yMax = Math.max(...data.sample_quantiles);

                // ✅ Compute OLS Line (y = slope * x + intercept)
                const olsLineX = [xMin, xMax];
                const olsLineY = olsLineX.map(x => data.slope * x + data.intercept);

                

                // ✅ Extract upper and lower bands directly from the backend response
                const upperBand = data.upper_band || [];
                const lowerBand = data.lower_band || [];

                // ✅ Generate a unique dynamic color for confidence bands
                const confColorRGB = [
                    Math.floor(Math.random() * 200 + 50), // Red (50-250)
                    Math.floor(Math.random() * 200 + 50), // Green (50-250)
                    Math.floor(Math.random() * 200 + 50)  // Blue (50-250)
                ];
                const confColor = `rgba(${confColorRGB.join(",")}, 0.3)`; // Light transparent color

   


                return (
                    <div className="qqplot-box" key={col}>
                        {/* ✅ Header with "View Stats" Button */}
                        <div className="qqplot-header">
                            <h4 className="qqplot-title" title={`${col} QQ-Plot`}>
                                {col.length > 52 ? col.slice(0, 52) + "..." : col} QQ-Plot
                            </h4>

                            {/* ✅ Toolbar with "View Stats" Button */}
                            <div className="qqplot-toolbar">
                                <button 
                                    className="view-stats-btn" 
                                    onClick={() => setShowQQPlotStats(prev => ({ ...prev, [col]: !prev[col] }))}
                                >
                                    📊 View Stats
                                </button>
                            </div>
                        </div>

                        {/* ✅ QQ-Plot Chart */}
                        <div className="qqplot-chart-container">
                        <Plot
    data={[
        // ✅ Sample Quantiles (Main Scatter Points)
        {
            x: data.theoretical_quantiles,
            y: data.sample_quantiles,
            type: "scatter",
            mode: "markers",
            marker: { color: sampleColor, size: 6, opacity: 0.8 },
            name: "Sample vs Theoretical Quantiles (qq)",
            hovertemplate: `
                <b style="color:${sampleColor};">Sample Quantiles</b><br>
                <b>Theoretical Quantile:</b> %{x:.3f}<br>
                <b>Sample Quantile:</b> %{y:.3f}
                <extra></extra>`,
        },

        // ✅ OLS Trend Line (Best-Fit)
        {
            x: olsLineX,
            y: olsLineY,
            type: "scatter",
            mode: "lines",
            line: { color: olsColor, width: 4, dash: "dash" }, // 🔥 Thicker line
            name: "OLS Fit Line",
            hovertemplate: `
                <b style="color:${olsColor};">OLS Fit Line</b><br>
                <b>Theoretical Quantile:</b> %{x:.3f}<br>
                <b>OLS Predicted Quantile:</b> %{y:.3f}
                <extra></extra>`,
        },


        // ✅ 95% Confidence Bands (Shaded Region) — FIXED to avoid affecting OLS line
        {
            x: [...data.theoretical_quantiles, ...data.theoretical_quantiles.slice().reverse()], // Close the shape
            y: [...upperBand, ...lowerBand.slice().reverse()], // Close the shape
            fill: "toself",
            fillcolor: confColor, // 🔥 Dynamically generated color
            line: { width: 0 }, // Hide border lines
            name: "95% Confidence Interval",
            hoverinfo: "skip", // Hide hover info for the confidence band
        },

        

        // ✅ Corrected Normality Line (45-degree reference, adjusted for y-range)
        {
            x: [Math.min(...data.theoretical_quantiles), Math.max(...data.theoretical_quantiles)],
            y: [Math.min(...data.sample_quantiles), Math.max(...data.sample_quantiles)], // 🔥 Proper scaling
            type: "scatter",
            mode: "lines",
            line: { color: normalityColor, width: 3, dash: "dot" }, // 🔥 Thicker line
            name: "Normality Line (Ideal)",
            hovertemplate: `
                <b style="color:${normalityColor};">Normality Line (Ideal)</b><br>
                <b>Theoretical Quantile:</b> %{x:.3f}<br>
                <b>Normal Expected Quantile:</b> %{y:.3f}
                <extra></extra>`,
        }
    ]}
    layout={{
        xaxis: { 
            title: "Theoretical Quantiles (Q)",
            range: [xMin, xMax],
            zeroline: false, // No zero line for better readability
        },
        yaxis: { 
            title: "Sample Quantiles (Q)",
            range: [yMin, yMax],
            zeroline: false,
        },
        legend: {
            x: 0.5,
            y: 1.15,
            xanchor: "center",
            yanchor: "bottom",
            orientation: "h",
        },
        hovermode: "x unified", // Ensures smooth hover experience
        autosize: false,
        width: 500,
        height: 400,
        margin: { l: 60, r: 60, t: 100, b: 120 },

        // ✅ Add the equation as a text annotation below the chart
        annotations: [
            {
                xref: "paper",
                yref: "paper",
                x: 0.5, // Centered horizontally
                y: -0.5, // Positioned below the chart
                showarrow: false,
                text: `<b>OLS Best-Fit Equation:</b> y(Q) = ${data.slope.toFixed(3)}x(Q) + ${data.intercept.toFixed(3)}`,
                font: { size: 14, color: "#2c3e50" }, // Styled for distinction
                align: "center",
            },
            {
                xref: "paper",
                yref: "paper",
                x: 0.5,
                y: -0.8, // Slightly below the equation
                showarrow: false,
                align: "center",
                text: `<b>Goodness of Fit (R²):</b> ${data.r_squared.toFixed(3)}<br>
                       ${
                           data.r_squared > 0.95 
                               ? "<span style='color:green;'>✅ Data closely follows a normal distribution</span>"
                               : data.r_squared >= 0.80
                               ? "<span style='color:orange;'>⚠️ Moderate fit, some deviations from normality</span>"
                               : "<span style='color:red;'>❌ Strong deviations from normality</span>"
                       }`,
                font: { size: 14, color: data.r_squared > 0.95 ? "green" : data.r_squared >= 0.80 ? "orange" : "red" },
            }
        ]        
        
        
        
    }}
    
    config={{
        responsive: true,
        displayModeBar: true,
        displaylogo: false,
        scrollZoom: true,
        modeBarButtonsToRemove: ["sendDataToCloud"],
    }}
/>





                        </div>

                       {/* ✅ Normality Statistics (Column-Specific Popup with Download Button) */}
{showQQPlotStats[col] && (
    <div className="qqplot-stats-popup">
        <div className="qqplot-stats-content">

            {/* 📥 Download Button */}
            <button 
                className="download-stats-btn" 
                onClick={() => downloadStatsAsCSV(col, data)}
                title="Download Stats as CSV"
            >
                ⬇️
            </button>

            {/* Column Label */}
            <h4 className="stats-column-label">{col} - Normality Statistics</h4>

            {/* Normality Metrics */}
            <table className="stats-table">
                <thead>
                    <tr>
                        <th>Metric</th>
                        <th>Value</th>
                    </tr>
                </thead>
                <tbody>
                    <tr><td>Mean</td><td>{safeFormat(data.mean, 2)}</td></tr>
                    <tr><td>Median</td><td>{safeFormat(data.median, 2)}</td></tr>
                    <tr><td>Standard Deviation</td><td>{safeFormat(data.std_dev)}</td></tr>
                    <tr><td>Variance</td><td>{safeFormat(data.variance)}</td></tr>
                    <tr><td>Skewness</td><td>{safeFormat(data.skewness)}</td></tr>
                    <tr><td>Kurtosis</td><td>{safeFormat(data.kurtosis)}</td></tr>
                    <tr><td>R² (Goodness of Fit)</td><td>{safeFormat(data.r_squared)}</td></tr>
                    <tr><td>Slope</td><td>{safeFormat(data.slope)}</td></tr>
                    <tr><td>Intercept</td><td>{safeFormat(data.intercept)}</td></tr>
                    <tr><td>Residual Std Error (RSE)</td><td>{safeFormat(data.residual_std_error)}</td></tr>
                </tbody>
            </table>

            {/* Normality Tests */}
            <h5>🧪 Normality Tests</h5>
            <table className="stats-table">
                <thead>
                    <tr>
                        <th>Test</th>
                        <th>Statistic</th>
                        <th>p-Value</th>
                    </tr>
                </thead>
                <tbody>
                    {Object.entries(data.normality_tests).map(([test, results]) => (
                        <tr key={test}>
                            <td>{test}</td>
                            <td>{results.statistic.toFixed(3)}</td>
                            <td>{results.p_value ? results.p_value.toExponential(2) : "N/A"}</td>
                        </tr>
                    ))}
                </tbody>
            </table>

            {/* Anderson-Darling Extra Data */}
            {data.normality_tests["Anderson-Darling"] && (
                <>
                    <h5>📊 Anderson-Darling Critical Values</h5>
                    <table className="stats-table">
                        <thead>
                            <tr>
                                <th>Significance Level (%)</th>
                                <th>Critical Value</th>
                            </tr>
                        </thead>
                        <tbody>
                            {data.normality_tests["Anderson-Darling"].critical_values.map((value, index) => (
                                <tr key={index}>
                                    <td>{data.normality_tests["Anderson-Darling"].significance_levels[index]}%</td>
                                    <td>{value.toFixed(3)}</td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </>
            )}

            {/* Close Button */}
            <button className="close-stats-btn" onClick={() => setShowQQPlotStats(prev => ({ ...prev, [col]: false }))}>
                Close
            </button>
        </div>
    </div>
)}





                        </div>
            
                );
            })}
        </div>
    </div>
)}

             






        


                









        </div>
    );
    
    
           
};

export default DistributionAnalysis;
