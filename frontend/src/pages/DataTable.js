import React, { useEffect, useState, useRef, useCallback } from "react";
import CustomHeader from "./CustomHeader";  // ✅ Import the custom header
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
    const [showFormattingMenu, setShowFormattingMenu] = useState(false);
    const [showDuplicateOptions, setShowDuplicateOptions] = useState(false)
    const [keepDropdownOpen, setKeepDropdownOpen] = useState(false);
    const dropdownRef = useRef(null);
    const [message, setMessage] = useState(""); // ✅ Stores success message
    const [messageType, setMessageType] = useState(""); // ✅ Type: success or error
    const [filteredData, setFilteredData] = useState(null); // Stores original dataset when filtering
    const [showingDuplicates, setShowingDuplicates] = useState(false); // Tracks filter state

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
                applyMiniFilterWhileTyping: true,},

            // ✅ Add dataType to column definitions
            dataType: col.dataType || "Unknown",
            headerComponent: CustomHeader, // ✅ Assign our custom header component
        }));
    };




    const detectDuplicates = async () => {
        if (!selectedSession) {
            console.error("❌ No dataset selected");
            return;
        }
    
        try {
            const response = await axios.get(`${API_URL}/api/detect_duplicates/${selectedSession}`);
            console.log("🔍 Duplicate Detection Response:", response.data);
    
            setMessage(response.data.message);
            setMessageType("success");
    
            // ✅ Close BOTH the sub-dropdown and main dropdown
            setShowFormattingMenu(false);
            setShowDuplicateOptions(false);
            setKeepDropdownOpen(false);
    
            setTimeout(() => setMessage(""), 5000);
        } catch (error) {
            console.error("❌ Error detecting duplicates:", error);
            setMessage("❌ Error detecting duplicates.");
            setMessageType("error");
    
            // ✅ Ensure the dropdown closes even if an error occurs
            setShowFormattingMenu(false);
            setShowDuplicateOptions(false);
            setKeepDropdownOpen(false);
    
            setTimeout(() => setMessage(""), 5000);
        }
    };






    // ✅ Function to Remove Duplicates
    const removeDuplicates = async () => {
        if (!selectedSession) {
            console.error("❌ No dataset selected");
            return;
        }
    
        try {
            const response = await axios.post(`${API_URL}/api/remove_duplicates/${selectedSession}`);
            console.log("🗑️ Remove Duplicates Response:", response.data);
    
            setMessage(response.data.message);
            setMessageType("success");
    
            // ✅ Refresh the dataset
            fetchData(selectedSession);
    
            // ✅ Close BOTH the sub-dropdown and main dropdown
            setShowFormattingMenu(false);
            setShowDuplicateOptions(false);
            setKeepDropdownOpen(false);
    
            setTimeout(() => setMessage(""), 5000);
        } catch (error) {
            console.error("❌ Error removing duplicates:", error);
            setMessage("❌ Failed to remove duplicates.");
            setMessageType("error");
    
            // ✅ Ensure the dropdown closes even if an error occurs
            setShowFormattingMenu(false);
            setShowDuplicateOptions(false);
            setKeepDropdownOpen(false);
    
            setTimeout(() => setMessage(""), 5000);
        }
    };




    const showOnlyDuplicates = () => {
        if (!rowData.length) {
            console.error("❌ No data available.");
            return;
        }
    
        // ✅ Count occurrences of each row
        const rowCounts = {};
        rowData.forEach(row => {
            const rowKey = JSON.stringify(row);
            rowCounts[rowKey] = (rowCounts[rowKey] || 0) + 1;
        });
    
        // ✅ Keep only duplicate rows
        const duplicatesOnly = rowData.filter(row => {
            const rowKey = JSON.stringify(row);
            return rowCounts[rowKey] > 1;
        });
    
        if (!duplicatesOnly.length) {
            // ✅ No duplicates found → Show message, but KEEP the table as is
            setMessage("🚫 No duplicate rows found.");
            setMessageType("warning");
    
            // ✅ Ensure the message disappears after 5 seconds
            setTimeout(() => setMessage(""), 5000);
            return; // ❌ Prevents toggling to "Restore All"
        }
    
        if (!showingDuplicates) {
            // ✅ Show only duplicate rows
            setFilteredData(rowData); // Store original data before filtering
            setRowData(duplicatesOnly);
            setMessage(`📌 Showing ${duplicatesOnly.length} duplicate rows.`);
            setShowingDuplicates(true);
        } else {
            // ✅ Restore original dataset
            setRowData(filteredData);
            setFilteredData(null);
            setMessage("✅ Restored all rows.");
            setShowingDuplicates(false);
        }
    
        setMessageType("success");
    
        // ✅ Hide message after 5 seconds
        setTimeout(() => setMessage(""), 5000);
    };
    


    // ✅ Handle dataset change
    const handleSessionChange = (event) => {
        const newSession = event.target.value;
        setSelectedSession(newSession);
    
        // ✅ Reset duplicate filtering state
        setFilteredData(null);
        setShowingDuplicates(false);
        setMessage(""); // ✅ Clear any messages
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
    
                {/* ✅ Formatting Button */}
                <div style={{ position: "relative", marginLeft: "20px" }} ref={dropdownRef}>
                    {/* ⚙️ Main Formatting Button */}
                    <button 
                        onClick={() => setShowFormattingMenu(prev => !prev)} 
                        className="formatting-button"
                    >
                        ⚙️ Formatting ▼
                    </button>

                    {/* ✅ Main Dropdown Menu */}
                    {showFormattingMenu && (
                        <div 
                            className="dropdown-menu"
                            onMouseEnter={() => setKeepDropdownOpen(true)}
                            onMouseLeave={() => setKeepDropdownOpen(false)}
                        >
                            {/* 🔍 Duplicates Submenu */}
                            <div 
                                className="dropdown-item"
                                onMouseEnter={() => setShowDuplicateOptions(true)}
                                onMouseLeave={() => setShowDuplicateOptions(false)}
                            >
                                🔍 Duplicates &rsaquo;

                                {/* ✅ Duplicates Submenu Options */}
                                {showDuplicateOptions && (
                                    <div 
                                        className="submenu"
                                        onMouseEnter={() => setShowDuplicateOptions(true)}
                                        onMouseLeave={() => setShowDuplicateOptions(false)}
                                    >
                                        {/* Detect Duplicates Button */}
                                        <button 
                                            className="submenu-item"
                                            onClick={() => {
                                                detectDuplicates();
                                                setShowFormattingMenu(false);  // ✅ Close menu
                                                setShowDuplicateOptions(false);
                                            }} 
                                        >
                                            🔍 Detect Duplicates
                                        </button>

                                        {/* Show / Restore Duplicates Button */}
                                        <button 
                                            className={`submenu-item ${showingDuplicates ? "restore-btn" : ""}`}  // ✅ Add conditional class
                                            onClick={() => {
                                                showOnlyDuplicates();  // ✅ Toggle duplicates
                                                setShowFormattingMenu(false);  
                                                setShowDuplicateOptions(false);
                                            }}
                                        >
                                            {showingDuplicates ? "🔄 Restore All" : "📌 Show Duplicates"}
                                        </button>

                                        {/* Remove Duplicates Button */}
                                        <button 
                                            className="submenu-item red"
                                            onClick={() => {
                                                removeDuplicates();
                                                setShowFormattingMenu(false);  
                                                setShowDuplicateOptions(false);
                                            }}
                                        >
                                            ❌ Remove Duplicates
                                        </button>
                                    </div>
                                )}
                            </div>
                        </div>
                    )}
                </div>


                {/* ✅ Export Buttons */}
                <div>
                    <button onClick={exportToCSV} style={{ marginRight: "10px" }}>Export CSV</button>
                    <button onClick={exportToExcel}>Export Excel</button>
                </div>
            </div>

            {/* ✅ Success/Error Message Box */}
            {message && (
                <div 
                    style={{
                        padding: "10px",
                        marginBottom: "10px",
                        borderRadius: "5px",
                        textAlign: "center",
                        fontSize: "16px",
                        fontWeight: "bold",
                        backgroundColor: messageType === "success" ? "#d4edda" : "#f8d7da",
                        color: messageType === "success" ? "#155724" : "#721c24",
                        border: messageType === "success" ? "1px solid #c3e6cb" : "1px solid #f5c6cb",
                    }}
                >
                    {message}
                </div>
            )}

    
            {/* ✅ AgGrid Table */}
            <AgGridReact
                ref={gridRef}
                onGridReady={(params) => (gridRef.current = params.api)}
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
                singleClickEdit={true}  // ✅ Enable single-click editing
                stopEditingWhenCellsLoseFocus={true}  // ✅ Save changes automatically

                
                
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