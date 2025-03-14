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







    const visualizationMethods = [
        { label: "Histogram", value: "histogram" },    
        { label: "Box Plot", value: "boxplot" },
        { label: "Violin Plot", value: "violin" },
        { label: "Pie Chart", value: "pie" },
        { label: "Bar Plot", value: "bar" },
        { label: "Scatterplot", value: "scatter" },
        { label: "QQ-Plot", value: "qqplot" },
        { label: "ECDF", value: "ecdf" },
        { label: "Facet Grid View", value: "facetgrid" },
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
                setBoxPlotData(null); // Clear box plot data
            } else if (selectedVisualization === "boxplot" && response.data.box_plots) {
                setBoxPlotData(response.data.box_plots);
                setHistogramData(null); // Clear histogram data


            } else {
                setError("No data received from the server.");
            }
        } catch (err) {
            console.error("Error fetching distribution plot:", err);
            setError("Failed to fetch distribution plot.");
        } finally {
            setLoading(false);
        }
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
                                        // Histogram bars
                                        {
                                            x: data.bins,
                                            y: data.frequencies,
                                            type: "bar",
                                            name: `${col}`,
                                            marker: { color: ["blue", "grey", "green", "purple", "red", "orange", "lemon", "darkblue", "brown"][index % 9] },
                                            hoverinfo: "skip",
                                            hovertemplate: `<b>${col.length > 20 ? col.slice(0, 20) + "..." : col}</b><br>%{x}<br>Freq: %{y}<extra></extra>`,
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
                                        // Median Line (Dotted Vertical Line) with Dynamic Hover Box
                                        {
                                            x: [data.median, data.median], // Single vertical line at median
                                            y: [0, Math.max(...data.frequencies) * 1.1], // Extends from bottom to top
                                            type: "scatter",
                                            mode: "lines",
                                            name: "Median",
                                            line: {
                                                color: ["#E91E63", "#9C27B0", "#673AB7", "#3F51B5", "#009688"][index % 5], // Unique colors
                                                width: 2.5,
                                                dash: "dot", // Dotted line
                                            },
                                            hoverinfo: "x",
                                            hovertemplate: `<b>Median: </b>%{x}</b><extra></extra>`, // Shows "Median: [value]"
                                        },

                                        // Mean Line (Dashed Vertical Line)
                                        {
                                            x: [data.mean, data.mean], // Single vertical line at mean
                                            y: [0, Math.max(...data.frequencies) * 1.1], // Full height
                                            type: "scatter",
                                            mode: "lines",
                                            name: "Mean",
                                            line: {
                                                color: ["#FFA500", "#FFC107", "#FF9800", "#FF5722", "#FF4500"][index % 5], // Unique colors
                                                width: 2.5,
                                                dash: "dash", // Dashed line for mean
                                            },
                                            hoverinfo: "x",
                                            hovertemplate: `<b>Mean: </b>%{x}</b><extra></extra>`,

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
                                    const medianColor = "#E91E63"; // Distinct median line color

                                    return (
                                        <div className="boxplot-box" key={col}>
                                            {/* ✅ Title */}
                                            <div className="boxplot-header">
                                                <h4 
                                                    className="boxplot-title" 
                                                    data-full-title={`${col} Box Plot`} /* Full title for tooltip */
                                                    title={`${col} box plot`} /* Fallback tooltip */
                                                >
                                                    {col.length > 52 ? col.slice(0, 52) + "..." : col} box plot
                                                </h4>
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
                                                        
                                                                // Truncate column name if it's too long (limit: 30 characters)
                                                                const maxLength = 21;
                                                                let truncatedColumnName = columnName.length > maxLength 
                                                                    ? columnName.substring(0, maxLength) + "..." 
                                                                    : columnName;
                                                        
                                                                if (params.seriesType === "boxplot") {
                                                                    return `
                                                                        <b>${truncatedColumnName} Box Plot</b><br>
                                                                        Min: ${data.min}<br>
                                                                        Q1: ${data.q1}<br>
                                                                        Median: ${data.median}<br>
                                                                        Q3: ${data.q3}<br>
                                                                        Max: ${data.max}
                                                                    `;
                                                                } else if (params.seriesType === "scatter") {
                                                                    return `<b>Outlier</b>: ${params.data[1]}`;
                                                                }
                                                            },
                                                        },   
                                                        
                                                        toolbox: {
                                                            show: true,
                                                            feature: {
                                                                saveAsImage: { show: true, title: "Save", filename: "boxplot", pixelRatio: 2 }, // 📷 Save Screenshot

                                                                restore: { show: true, title: "Reset View" }, // 🔄 Reset Zoom/State
                                                                
                                                                     dataView: { 
                                                                        show: true, 
                                                                        title: "View Data",
                                                                        readOnly: true, // Prevent editing
                                                                        lang: ["Box Plot Data", "Close", "Refresh"],
                                                                        optionToContent: function(opt) {
                                                                            const series = opt.series[0]; // Extract first series (box plot)
                                                                            const table = document.createElement("table");
                                                                            table.style.borderCollapse = "collapse";
                                                                            table.style.width = "100%";
                                                                            table.style.textAlign = "center";
                                                            
                                                                            // ✅ Define Headers
                                                                            const headers = ["Column", "Min", "Q1", "Median", "Q3", "Max"];
                                                                            let headerRow = "<tr style='font-weight: bold; background: #f5f5f5;'>";
                                                                            headers.forEach(header => {
                                                                                headerRow += `<th style='border: 1px solid #ccc; padding: 5px;'>${header}</th>`;
                                                                            });
                                                                            headerRow += "</tr>";
                                                            
                                                                            // ✅ Add Data Rows
                                                                            let rows = "";
                                                                            series.data.forEach((data, index) => {
                                                                                rows += "<tr>";
                                                                                rows += `<td style='border: 1px solid #ccc; padding: 5px;'>${opt.xAxis[0].data[index]}</td>`; // Column Name
                                                                                data.forEach(value => {
                                                                                    rows += `<td style='border: 1px solid #ccc; padding: 5px;'>${value}</td>`;
                                                                                });
                                                                                rows += "</tr>";
                                                                            });
                                                            
                                                                            table.innerHTML = `<thead>${headerRow}</thead><tbody>${rows}</tbody>`;
                                                                            return table.outerHTML;
                                                                        }
                                                                    }
                                                                 
                                                                
                                                            },
                                                            right: "5%", // Align to the right
                                                            top: "5%", // Align to the top
                                                        },

                                                        
                                                        
                                                        xAxis: {
                                                            type: "category",
                                                            data: [col],
                                                            axisLabel: { rotate: 45 },
                                                        },
                                                        yAxis: {
                                                            type: "value",
                                                            name: "Values",
                                                        },
                                                        series: [
                                                            // Box plot series with dynamic colors
                                                            {
                                                                name: "Box Plot",
                                                                type: "boxplot",
                                                                data: [[data.min, data.q1, data.median, data.q3, data.max]],
                                                                itemStyle: { color: boxColor },
                                                                
                                                                
                                                            },
                                                            // Median line (Always distinct from box color)
                                                            {
                                                                name: "Median",
                                                                type: "scatter",
                                                                data: [[col, data.median]],
                                                                symbol: "diamond",
                                                                symbolSize: 10,
                                                                itemStyle: { color: medianColor },
                                                            },
                                                            // Outlier series
                                                            {
                                                                name: "Outliers",
                                                                type: "scatter",
                                                                data: data.outliers.map((value) => [col, value]),
                                                                symbolSize: 10,
                                                                itemStyle: { color: "red" },
                                                            },
                                                        ],
                                                        // ❌ Remove legend
                                                        legend: {
                                                            show: false,
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
        


                









        </div>
    );
    
    
           
};

export default DistributionAnalysis;

