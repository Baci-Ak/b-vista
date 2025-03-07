import React, { useState, useEffect } from "react";
import axios from "axios";
import Plot from "react-plotly.js";

const API_URL = "http://127.0.0.1:5050"; // ✅ Your backend URL

const CorrelationMatrix = () => {
    const [columns, setColumns] = useState([]); // Store available columns
    const [selectedColumns, setSelectedColumns] = useState([]); // User-selected columns
    const [correlationData, setCorrelationData] = useState(null); // Correlation matrix

    // ✅ Fetch available columns from the backend
    useEffect(() => {
        const fetchColumns = async () => {
            try {
                const response = await axios.get(`${API_URL}/api/get_columns`);
                if (response.data.columns) {
                    setColumns(response.data.columns);
                    setSelectedColumns(response.data.columns.slice(0, 5)); // Default: First 5 columns
                }
            } catch (err) {
                console.error("❌ Error fetching columns:", err);
            }
        };

        fetchColumns();
    }, []);

    // ✅ Handle column selection
    const handleColumnToggle = (column) => {
        setSelectedColumns((prev) =>
            prev.includes(column)
                ? prev.filter((col) => col !== column) // Remove if already selected
                : [...prev, column] // Add if not selected
        );
    };

    // ✅ Fetch correlation data when selectedColumns change
    useEffect(() => {
        if (selectedColumns.length === 0) return;

        const fetchCorrelation = async () => {
            try {
                const response = await axios.post(`${API_URL}/api/correlation_matrix`, {
                    columns: selectedColumns,
                });
                if (response.data.matrix) {
                    setCorrelationData(response.data.matrix);
                }
            } catch (err) {
                console.error("❌ Error fetching correlation matrix:", err);
            }
        };

        fetchCorrelation();
    }, [selectedColumns]);

    return (
        <div style={{ padding: "20px" }}>
            <h2>🔗 Correlation Matrix</h2>

            {/* Column Selection */}
            <div>
                <h4>Select Columns:</h4>
                {columns.map((col) => (
                    <label key={col} style={{ marginRight: "10px" }}>
                        <input
                            type="checkbox"
                            checked={selectedColumns.includes(col)}
                            onChange={() => handleColumnToggle(col)}
                        />
                        {col}
                    </label>
                ))}
            </div>

            {/* Correlation Heatmap */}
            {correlationData && (
                <Plot
                    data={[
                        {
                            z: correlationData.values,
                            x: correlationData.columns,
                            y: correlationData.columns,
                            type: "heatmap",
                            colorscale: "Viridis",
                        },
                    ]}
                    layout={{
                        title: "Correlation Heatmap",
                        autosize: true,
                    }}
                />
            )}
        </div>
    );
};

export default CorrelationMatrix;
