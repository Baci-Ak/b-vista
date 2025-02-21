import React, { useEffect, useState, useRef, useCallback } from "react";
import axios from "axios";
import { io } from "socket.io-client";
import { AgGridReact } from "ag-grid-react";
import "ag-grid-community/styles/ag-grid.css";
import "ag-grid-community/styles/ag-theme-alpine.css";
import { ModuleRegistry } from "ag-grid-enterprise";
import {
    ClientSideRowModelModule,
    MenuModule,
    IntegratedChartsModule,
    RangeSelectionModule,
    ColumnsToolPanelModule,
    FiltersToolPanelModule,
    ClipboardModule,
    ExcelExportModule,
    RowGroupingModule,
    SetFilterModule,
} from "ag-grid-enterprise";

// ✅ Register AgGrid modules
ModuleRegistry.registerModules([
    ClientSideRowModelModule,
    MenuModule,
    ColumnsToolPanelModule,
    FiltersToolPanelModule,
    ClipboardModule,
    IntegratedChartsModule,
    RangeSelectionModule,
    ExcelExportModule,
    RowGroupingModule,
    SetFilterModule,
]);

const API_URL = "http://127.0.0.1:5050";  // ✅ Backend API URL

function DataTable() {
    const [rowData, setRowData] = useState([]);  // ✅ Holds table data
    const [columnDefs, setColumnDefs] = useState([]);  // ✅ Holds column definitions
    const [sessions, setSessions] = useState([]);  // ✅ Holds available datasets
    const [selectedSession, setSelectedSession] = useState(null);  // ✅ Tracks selected dataset
    const [datasetShape, setDatasetShape] = useState("(0, 0)");  // ✅ Stores dataset shape from backend
    const gridRef = useRef();  // ✅ Reference to AgGrid instance

    // ✅ Fetch dataset from backend
    const fetchData = useCallback(async (sessionId) => {
        if (!sessionId) return;
        try {
            console.log(`📡 Fetching data for session: ${sessionId}`);
            const response = await axios.get(`${API_URL}/api/session/${sessionId}`);
            console.log("🔄 API Response:", response.data);

            if (response.data.data) {
                setRowData(response.data.data);
                setColumnDefs(formatColumnDefs(response.data.columns));
                
                // ✅ Fetch shape directly from backend
                setDatasetShape(`(${response.data.total_rows || 0}, ${response.data.total_columns || 0})`);
            } else {
                console.error("⚠️ No data found in API response.");
            }
        } catch (err) {
            console.error("❌ Error fetching data:", err);
        }
    }, []);

    // ✅ Fetch available sessions (datasets)
    const fetchSessions = useCallback(async () => {
        try {
            const response = await axios.get(`${API_URL}/api/get_sessions`);
            if (response.data.sessions) {
                const sessionEntries = Object.entries(response.data.sessions).map(([id, session]) => ({
                    id,
                    name: session.name || `Dataset ${id}`,
                }));
                setSessions(sessionEntries);

                // ✅ Auto-select the latest dataset if none is selected
                if (sessionEntries.length > 0 && !selectedSession) {
                    const latestSession = sessionEntries[sessionEntries.length - 1].id;
                    setSelectedSession(latestSession);
                    fetchData(latestSession);
                }
            }
        } catch (err) {
            console.error("❌ Error fetching sessions:", err);
        }
    }, [fetchData, selectedSession]);

    // ✅ Handle first-time data fetch
    useEffect(() => {
        fetchSessions();
    }, [fetchSessions]);

    // ✅ Handle dataset selection change
    useEffect(() => {
        if (selectedSession) {
            fetchData(selectedSession);
        }
    }, [selectedSession, fetchData]);

    // ✅ Real-time updates via WebSockets
    useEffect(() => {
        const socket = io(API_URL);
        socket.on("update_data", (newData) => {
            fetchSessions();
            if (newData.session_id === selectedSession) {
                setRowData(newData.data);
            }
        });
        return () => {
            socket.disconnect();
        };
    }, [selectedSession, fetchSessions]);

    // ✅ Format column definitions
    const formatColumnDefs = (columns = []) => {
        return columns.map((col) => ({
            field: col.field,
            headerName: col.headerName,
            editable: true,
            filter: "agSetColumnFilter",
            floatingFilter: true,
            resizable: true,
            sortable: true,
            enableValue: true,
            enableRowGroup: true,
            enablePivot: true,
            menuTabs: ["filterMenuTab", "columnsMenuTab"],
            suppressMenu: false,
            filterParams: {
                suppressMiniFilter: false,
                applyMiniFilterWhileTyping: true,
            },
        }));
    };

    // ✅ Handle dataset change
    const handleSessionChange = (event) => {
        setSelectedSession(event.target.value);
    };

    // ✅ Export functions
    const exportToCSV = () => gridRef.current.exportDataAsCsv();
    const exportToExcel = () => gridRef.current.exportDataAsExcel();

    return (
        <div className="ag-theme-alpine" style={{ height: "650px", width: "100%", padding: "15px", borderRadius: "8px", boxShadow: "0 4px 8px rgba(0,0,0,0.1)" }}>
            <h2>📊 Data Table</h2>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "10px" }}>
                
                {/* ✅ Dataset Selection & Shape Display */}
                <div style={{ display: "flex", alignItems: "center", gap: "15px" }}>
                    <div>
                        <label>Select Dataset: </label>
                        <select onChange={handleSessionChange} value={selectedSession}>
                            {sessions.map((session) => (
                                <option key={session.id} value={session.id}>{session.name}</option>
                            ))}
                        </select>
                    </div>

                    {/* ✅ Dataset Shape Display Box (Backend-controlled) */}
                    <div 
                        style={{ 
                            padding: "5px 10px",
                            border: "1px solid #ccc",
                            borderRadius: "5px",
                            background: "#f9f9f9",
                            fontSize: "14px",
                            fontWeight: "bold"
                        }}
                    >
                        {datasetShape}
                    </div>
                </div>

                {/* ✅ Export Buttons */}
                <div>
                    <button onClick={exportToCSV} style={{ marginRight: "10px" }}>Export CSV</button>
                    <button onClick={exportToExcel}>Export Excel</button>
                </div>
            </div>

            {/* ✅ AgGrid Table */}
            <AgGridReact
                ref={gridRef}
                rowData={rowData}
                columnDefs={columnDefs}
                pagination={true}
                paginationPageSize={10}
                animateRows={true}
                rowSelection="multiple"
                suppressMenuHide={true}
                suppressHorizontalScroll={false}
                enableRangeSelection={true}
                enableClipboard={true}
                sideBar={{
                    toolPanels: [
                        { id: "columns", labelDefault: "Columns", toolPanel: "agColumnsToolPanel", minWidth: 300 },
                        { id: "filters", labelDefault: "Filters", toolPanel: "agFiltersToolPanel", minWidth: 300 },
                    ],
                    defaultToolPanel: "columns",
                }}
                rowGroupPanelShow="always"
                pivotPanelShow="always"
                groupDisplayType="groupRows"
                defaultColDef={{
                    sortable: true,
                    resizable: true,
                    editable: true,
                    floatingFilter: true,
                    filter: "agSetColumnFilter",
                    enableValue: true,
                    enableRowGroup: true,
                    enablePivot: true,
                }}
            />
        </div>
    );
}

export default DataTable;
