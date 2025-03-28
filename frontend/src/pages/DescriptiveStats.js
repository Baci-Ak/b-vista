import React, { useState, useEffect, useRef } from "react";
//import "./DescriptiveStats.css"; // ✅ Ensure styling exists

import axios from "axios";
import { AgGridReact } from "ag-grid-react";
import "ag-grid-community/styles/ag-grid.css";
import "ag-grid-community/styles/ag-theme-alpine.css";
import { ModuleRegistry } from "ag-grid-enterprise";
import {
    ClientSideRowModelModule,
    MenuModule,
    ColumnsToolPanelModule,
    FiltersToolPanelModule,
    ClipboardModule,
    ExcelExportModule,
    RowGroupingModule,
    SetFilterModule,
} from "ag-grid-enterprise";
//import "./DescriptiveStats.css"; // ✅ Ensure styling exists

const API_URL = "http://127.0.0.1:5050"; // ✅ Backend API URL

// ✅ Register AG Grid Enterprise modules
ModuleRegistry.registerModules([
    ClientSideRowModelModule,
    MenuModule,
    ColumnsToolPanelModule,
    FiltersToolPanelModule,
    ClipboardModule,
    ExcelExportModule,
    RowGroupingModule,
    SetFilterModule,
]);

const DescriptiveStats = () => {
    const [selectedSession, setSelectedSession] = useState(null);
    const [sessions, setSessions] = useState([]);
    const [datasetShape, setDatasetShape] = useState("(0, 0)");
    const [descriptiveStats, setDescriptiveStats] = useState(null);
    const gridRef = useRef(); // ✅ AG Grid Reference
    

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
                    if (sessionEntries.length > 0) {
                        setSelectedSession(sessionEntries[sessionEntries.length - 1].id);
                    }
                }
            } catch (err) {
                console.error("❌ Error fetching sessions:", err);
            }
        };

        fetchSessions();
    }, []);

    // ✅ Fetch dataset shape
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

    // ✅ Fetch descriptive statistics
    useEffect(() => {
        if (!selectedSession) return;

        const fetchDescriptiveStats = async () => {
            try {
                const response = await axios.get(`${API_URL}/api/descriptive_stats/${selectedSession}`);
                if (response.data.statistics) {
                    console.log("📊 Descriptive Statistics:", response.data.statistics);
                    setDescriptiveStats(response.data.statistics);
                }
            } catch (err) {
                console.error("❌ Error fetching descriptive statistics:", err);
            }
        };

        fetchDescriptiveStats();
    }, [selectedSession]);

    // ✅ Convert descriptive statistics data into AG Grid format
    const columnDefs = descriptiveStats
        ? [
              { headerName: "Statistic", field: "statistic", pinned: "left", width: 200 },
              ...Object.keys(descriptiveStats).map((col) => ({
                  headerName: col,
                  field: col,
                  resizable: true,
                  //sortable: true,
              })),
          ]
        : [];

        const rowData = descriptiveStats
    ? Object.keys(descriptiveStats[Object.keys(descriptiveStats)[0]] || {}).map((stat) => {
          let row = { statistic: stat };
          Object.keys(descriptiveStats).forEach((col) => {
              row[col] = descriptiveStats[col][stat]; // ✅ Directly pass values from backend
          });
          return row;
      })
    : [];





    // ✅ Export Data
    const exportCSV = () => gridRef.current.api.exportDataAsCsv();
    const exportExcel = () => gridRef.current.api.exportDataAsExcel();

    return (
        <div className="ag-theme-alpine" style={{ height: "650px", width: "100%", padding: "15px", borderRadius: "8px", boxShadow: "0 4px 8px rgba(0,0,0,0.1)" }}>
            <h2>📊 Descriptive Statistics</h2>

            {/* ✅ Dataset Selection & Shape Display */}
            <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: "10px" }}>
                <div>
                    <label>Select Dataset: </label>
                    <select onChange={(e) => setSelectedSession(e.target.value)} value={selectedSession}>
                        {sessions.map((session) => (
                            <option key={session.id} value={session.id}>{session.name}</option>
                        ))}
                    </select>
                </div>

                {/* ✅ Dataset Shape */}
                <div
                    style={{
                        /*padding: "5px 10px",*/
                        border: "1px solid #ccc",
                        borderRadius: "5px",
                        background: "#f9f9f9",
                        fontSize: "15px",
                        fontWeight: "bold",
                    }}
                >
                    {datasetShape}
                </div>

                {/* ✅ Export Buttons */}
                <div>
                    <button onClick={exportCSV} style={{ marginRight: "10px" }}>Export CSV</button>
                    <button onClick={exportExcel}>Export Excel</button>
                </div>
            </div>

            {/* ✅ AG Grid Table */}
            <AgGridReact
                ref={gridRef}
                rowData={rowData}
                columnDefs={columnDefs}
                pagination={true}
                paginationPageSize={50}
                cacheBlockSize={50}
                animateRows={true}
                rowBuffer={10}
                suppressHorizontalScroll={false}
                enableRangeSelection={true}
                enableClipboard={true}
                
                //rowGroupPanelShow="always"
                //pivotPanelShow="always"
                //groupDisplayType="groupRows"
                defaultColDef={{
                    sortable: true,
                    resizable: true,
                    editable: false,
                    floatingFilter: true,
                    filter: "agSetColumnFilter",
                    //enableValue: true,
                    //enableRowGroup: true,
                    //enablePivot: true,
                    menuTabs: ["filterMenuTab", "columnsMenuTab", "generalMenuTab"],
                }}
            />
        </div>
    );
};

export default DescriptiveStats;
