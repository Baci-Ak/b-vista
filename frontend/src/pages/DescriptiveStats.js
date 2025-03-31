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
import "./DescriptiveStats.css"; // ✅ Ensure styling exists

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
              { headerName: "Statistic", field: "statistic", pinned: "left", width: 200, cellClass: "statistic-column-cell", headerClass: "statistic-column-header" },    
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





    // ✅ Export to CSV
    const exportCSV = () => {
        if (gridRef.current) {
        gridRef.current.api.exportDataAsCsv();
        }
    };
    
    // ✅ Export to Excel
    const exportExcel = () => {
        if (gridRef.current) {
        gridRef.current.api.exportDataAsExcel();
        }
    };
  

    return (
        <div className="descriptive-stats-page">
          {/* ✅ Header */}
          <div className="descriptive-header">📊 Descriptive Statistics</div>
      
          {/* ✅ Dataset Selection */}
          <div className="descriptive-dataset-selection">
            <div>
              <label>Select Dataset: </label>
              <select onChange={(e) => setSelectedSession(e.target.value)} value={selectedSession} className="descriptive-dropdown">
                {sessions.map((session) => (
                  <option key={session.id} value={session.id}>
                    {session.name}
                  </option>
                ))}
              </select>
            </div>
            <div className="descriptive-shape">{datasetShape}</div>
          </div>
      
          {/* ✅ Grid & Export Buttons */}
          <div className="descriptive-grid-wrapper">
            <div className="descriptive-export-buttons">
              <button className="descriptive-export-btn" onClick={exportCSV} title="Export CSV">
                📄
              </button>
              <button className="descriptive-export-btn" onClick={exportExcel} title="Export Excel">
                📊
              </button>
            </div>
      
            <div className="ag-theme-alpine-descriptive">
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
                domLayout="normal"
                defaultColDef={{
                  sortable: true,
                  resizable: true,
                  editable: false,
                  floatingFilter: true,
                  filter: "agSetColumnFilter",
                  menuTabs: ["filterMenuTab", "columnsMenuTab", "generalMenuTab"],
                }}
              />
            </div>
          </div>
        </div>
      );
      
};

export default DescriptiveStats;