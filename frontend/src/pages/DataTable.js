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

const API_URL = "http://127.0.0.1:5050";

function DataTable() {
    const [rowData, setRowData] = useState([]);
    const [columnDefs, setColumnDefs] = useState([]);
    const [sessions, setSessions] = useState([]);
    const [selectedSession, setSelectedSession] = useState(null);
    const gridRef = useRef();

    const fetchData = useCallback(async (sessionId) => {
        if (!sessionId) return;
        try {
            console.log(`📡 Fetching data for session: ${sessionId}`);
            const response = await axios.get(`${API_URL}/api/session/${sessionId}`);
            console.log("🔄 API Response:", response.data);

            if (response.data.data) {
                setRowData(response.data.data);
                setColumnDefs(formatColumnDefs(response.data.columns));
            } else {
                console.error("⚠️ No data found in API response.");
            }
        } catch (err) {
            console.error("❌ Error fetching data:", err);
        }
    }, []);

    const fetchSessions = useCallback(async () => {
        try {
            const response = await axios.get(`${API_URL}/api/get_sessions`);
            if (response.data.sessions) {
                const sessionEntries = Object.entries(response.data.sessions).map(([id, session]) => ({
                    id,
                    name: session.name || `Dataset ${id}`,
                }));
                setSessions(sessionEntries);
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

    useEffect(() => {
        fetchSessions();
    }, [fetchSessions]);

    useEffect(() => {
        if (selectedSession) {
            fetchData(selectedSession);
        }
    }, [selectedSession, fetchData]);

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

    const formatColumnDefs = (columns = []) => {
        return columns.map((col) => ({
            field: col.field,
            headerName: col.headerName,
            editable: true,
            filter: "agTextColumnFilter",
            floatingFilter: true,
            resizable: true,
            sortable: true,
        }));
    };

    const handleSessionChange = (event) => {
        setSelectedSession(event.target.value);
    };

    return (
        <div className="ag-theme-alpine" style={{ height: "650px", width: "100%", padding: "15px", borderRadius: "8px", boxShadow: "0 4px 8px rgba(0,0,0,0.1)" }}>
            <h2>📊 Data Table</h2>
            <div>
                <label>Select Dataset: </label>
                <select onChange={handleSessionChange} value={selectedSession}>
                    {sessions.map((session) => (
                        <option key={session.id} value={session.id}>{session.name}</option>
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
                suppressMenuHide={true}
                suppressHorizontalScroll={false}
                sideBar={{
                    toolPanels: [
                        { id: "columns", labelDefault: "Columns", toolPanel: "agColumnsToolPanel", minWidth: 300 },
                        { id: "filters", labelDefault: "Filters", toolPanel: "agFiltersToolPanel", minWidth: 300 },
                    ],
                    defaultToolPanel: "filters",
                }}
                defaultColDef={{
                    sortable: true,
                    resizable: true,
                    editable: true,
                    floatingFilter: true,
                    filter: "agTextColumnFilter",
                }}
            />
        </div>
    );
}

export default DataTable;
