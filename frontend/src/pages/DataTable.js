import React, { useEffect, useState, useRef, useCallback } from "react";
import axios from "axios";
import { io } from "socket.io-client";
import { AgGridReact } from "ag-grid-react";
import "ag-grid-community/styles/ag-grid.css";
import "ag-grid-community/styles/ag-theme-alpine.css";
import { ModuleRegistry } from "ag-grid-community";
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

// ✅ Register AG Grid Modules
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

let API_URL = "http://127.0.0.1:5050"; // Default backend URL

function DataTable() {
    const [rowData, setRowData] = useState([]);
    const [columnDefs, setColumnDefs] = useState([]);
    const [sessions, setSessions] = useState([]);
    const [selectedSession, setSelectedSession] = useState(null);
    const gridRef = useRef();

    // ✅ Fetch Data Function (Load dataset when session changes)
    const fetchData = useCallback(async (sessionId) => {
        if (!sessionId) return;
        try {
            console.log(`📡 Fetching data for session: ${sessionId}`);
            const response = await axios.get(`${API_URL}/api/get_data?session_id=${sessionId}`);
            if (response.data.status === "success") {
                setRowData(response.data.data);
                setColumnDefs(formatColumnDefs(response.data.columns));
            } else {
                console.error("Error fetching data:", response.data.message);
            }
        } catch (err) {
            console.error("Error fetching data:", err);
        }
    }, []);

    // ✅ Fetch Available Sessions from Backend
    const fetchSessions = useCallback(async () => {
        try {
            console.log("📡 Fetching available sessions...");
            const response = await axios.get(`${API_URL}/api/get_sessions`);
            if (response.data.status === "success") {
                const sessionEntries = Object.entries(response.data.sessions);
                setSessions(sessionEntries);

                // ✅ Ensure first session is selected if none is selected
                if (sessionEntries.length > 0 && !selectedSession) {
                    const latestSession = sessionEntries[sessionEntries.length - 1][0]; // Get last session
                    setSelectedSession(latestSession);
                    fetchData(latestSession); // Load data for the latest session
                }
            } else {
                console.error("Error fetching sessions:", response.data.message);
            }
        } catch (err) {
            console.error("Error fetching sessions:", err);
        }
    }, [fetchData, selectedSession]); // ✅ Now includes `fetchData` dependency

    // ✅ Fetch sessions when component mounts
    useEffect(() => {
        fetchSessions();
    }, [fetchSessions]); // ✅ Ensures sessions load when the component mounts

    // ✅ Fetch Data when session changes
    useEffect(() => {
        if (selectedSession) {
            fetchData(selectedSession);
        }
    }, [selectedSession, fetchData]);

    // ✅ WebSocket for Live Data Updates
    useEffect(() => {
        const socket = io(API_URL);
        socket.on("data_update", (newData) => {
            console.log("🔄 Data Update Received:", newData);
            fetchSessions(); // Ensure sessions are updated when new data is added
            if (newData.session_id === selectedSession) {
                setRowData(newData.data);
            }
        });
        return () => {
            socket.disconnect();
        };
    }, [selectedSession, fetchSessions]); // ✅ Ensures WebSocket updates when session changes

    // ✅ Format Column Definitions
    const formatColumnDefs = (columns = []) => {
        return columns.map((col) => ({
            field: col.field,
            headerName: col.headerName,
            editable: true,
            filter: "agSetColumnFilter",
            floatingFilter: true,
            resizable: true,
            sortable: true,
        }));
    };

    // ✅ Handle Session Dropdown Change
    const handleSessionChange = (event) => {
        setSelectedSession(event.target.value);
    };

    return (
        <div className="ag-theme-alpine" style={{ height: "650px", width: "100%", overflowX: "auto", padding: "15px", borderRadius: "8px", boxShadow: "0 4px 8px rgba(0,0,0,0.1)" }}>
            <h2>📊 Data Table</h2>
            <div>
                <label>Select Dataset: </label>
                <select onChange={handleSessionChange} value={selectedSession}>
                    {sessions.map(([id, session]) => (
                        <option key={id} value={id}>{session.name}</option>
                    ))}
                </select>
            </div>
            <AgGridReact
                ref={gridRef}
                rowData={rowData}
                columnDefs={columnDefs}
                pagination={true}
                paginationPageSize={10}
                animateRows={true}
                rowSelection="multiple"
                enableRangeSelection={true}
                enableCharts={true}
                enableClipboard={true}
                suppressMenuHide={true}
                suppressHorizontalScroll={false}
                defaultColDef={{
                    sortable: true,
                    resizable: true,
                    editable: true,
                    floatingFilter: true,
                    filter: "agSetColumnFilter",
                }}
                sideBar={{
                    toolPanels: [
                        { id: "columns", labelDefault: "Columns", toolPanel: "agColumnsToolPanel", minWidth: 300 },
                        { id: "filters", labelDefault: "Filters", toolPanel: "agFiltersToolPanel", minWidth: 300 },
                    ],
                    defaultToolPanel: "filters",
                }}
            />
        </div>
    );
}

export default DataTable;
