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
    const [showConvertTypeMenu, setShowConvertTypeMenu] = useState(false);
    const [showColumnSelectionMenu, setShowColumnSelectionMenu] = useState(false);
    const [columnSearch, setColumnSearch] = useState("");  // Search filter for column selection
    const [selectedColumnToConvert, setSelectedColumnToConvert] = useState("");  // Stores the selected column
    const [selectedDataType, setSelectedDataType] = useState("");  // Stores the new data type
    const columnMenuRef = useRef(null);
    const dataTypeMenuRef = useRef(null);
    const [selectedCurrencySymbol, setSelectedCurrencySymbol] = useState("$");

    const [showDataTypeMenu, setShowDataTypeMenu] = useState(false);  // Data type selection dropdown
    const [showReplaceMenu, setShowReplaceMenu] = useState(false);
    const [selectedColumnToReplace, setSelectedColumnToReplace] = useState("");
    const [replaceValue, setReplaceValue] = useState("");
    const [newReplaceValue, setNewReplaceValue] = useState("");





    



    // ✅ Fetch dataset from backend
    const fetchData = useCallback(async (sessionId) => {
        if (!sessionId) return;
        try {
            console.log(`📡 Fetching fresh data for session: ${sessionId}`);
    
            // ✅ Force a fresh request by adding a timestamp to the URL (prevents caching)
            const response = await axios.get(`${API_URL}/api/session/${sessionId}?_=${new Date().getTime()}`);
            
            console.log("🔄 Updated API Response:", response.data);
    
            if (response.data.data) {
                setRowData(response.data.data); // ✅ Update table data
                setColumnDefs(formatColumnDefs(response.data.columns)); // ✅ Update column types
    
                // ✅ Force update dataset shape
                setDatasetShape(`(${response.data.total_rows || 0}, ${response.data.total_columns || 0})`);
            } else {
                console.error("⚠️ No data found in API response.");
            }
        } catch (err) {
            console.error("❌ Error fetching updated data:", err);
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
            filterParams: {suppressMiniFilter: false, applyMiniFilterWhileTyping: true },
            // ✅ Ensure proper currency and percentage formatting
            valueFormatter: (params) => {
                if (!params.value) return params.value;

                if (col.dataType === "currency") {
                    return params.value; // The backend already formats currency (e.g., "$1,234.56")
                }
                if (col.dataType === "percentage") {
                    return params.value; // The backend already formats percentage (e.g., "85.00%")
                }
                if (col.dataType === "date") {
                    return new Date(params.value).toLocaleDateString("en-US"); // Converts to MM/DD/YYYY
                }
                if (col.dataType === "time") {
                    return new Date("1970-01-01 " + params.value).toLocaleTimeString("en-US", { hour12: false }); // Converts to HH:MM:SS
                }
                if (col.dataType === "datetime64") {
                    return new Date(params.value).toLocaleString("en-US"); // Converts to MM/DD/YYYY HH:MM:SS
                }
                if (col.dataType === "float64") {
                    return Number.isInteger(params.value) ? params.value.toFixed(1) : params.value;
                }
                return params.value;
            },
            

            // ✅ Dynamically set the data type
            dataType: col.dataType,  
    
            // ✅ Ensure the custom header receives the correct data type
            headerComponent: CustomHeader,
            headerComponentParams: {
                dataType: col.dataType || "Unknown",  // ✅ Pass dataType to custom header
            }
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
    
            // ✅ Close dropdowns even if no duplicates are found
            setShowFormattingMenu(false);
            setShowDuplicateOptions(false);
            setKeepDropdownOpen(false);
    
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
    
        // ✅ Close dropdowns after selecting "Show Duplicates"
        setShowFormattingMenu(false);
        setShowDuplicateOptions(false);
        setKeepDropdownOpen(false);
    
        // ✅ Hide message after 5 seconds
        setTimeout(() => setMessage(""), 5000);
    };
    
    




    useEffect(() => {
        const handleClickOutside = (event) => {
            if (
                dropdownRef.current && !dropdownRef.current.contains(event.target)
            ) {
                setShowFormattingMenu(false);  // ✅ Closes "Formatting" dropdown when clicking outside
                setShowDuplicateOptions(false);
                setShowConvertTypeMenu(false);
            }
        };
    
        document.addEventListener("mousedown", handleClickOutside);
        return () => {
            document.removeEventListener("mousedown", handleClickOutside);
        };
    }, []);
    
    
    
    
    
    


    // ✅ Handle dataset change
    const handleSessionChange = (event) => {
        const newSession = event.target.value;
        setSelectedSession(newSession);
    
        // ✅ Reset duplicate filtering state
        setFilteredData(null);
        setShowingDuplicates(false);
        setMessage(""); // ✅ Clear any messages
    };




    const convertColumnDataType = () => {
        if (!selectedColumnToConvert || !selectedDataType) {
            setMessage("⚠️ Please select a column and a target data type.");
            setMessageType("warning");
            setTimeout(() => setMessage(""), 4000);
            return;
        }
    
        console.log(`🟢 Converting ${selectedColumnToConvert} to ${selectedDataType}...`); // ✅ Debugging Step 1
    
        // ✅ Prepare request payload
        let requestData = { 
            column: selectedColumnToConvert, 
            new_type: selectedDataType 
        };
    
        // ✅ Handle currency conversion separately
        if (selectedDataType === "currency") {
            requestData.currency_symbol = selectedCurrencySymbol || "$";  // Default to "$" if not provided
        }
    
        axios.post(`${API_URL}/api/convert_datatype/${selectedSession}`, requestData, {
            headers: { "Content-Type": "application/json" }  
        })
        .then(response => {
            console.log("✅ Backend Response:", response.data); // ✅ Debugging Step 2
            setMessage(`✅ Column "${selectedColumnToConvert}" converted to ${selectedDataType}`);
            setMessageType("success");
    
            // ✅ Ensure frontend reloads updated dataset
            setTimeout(() => {
                console.log("🔄 Fetching updated dataset..."); // ✅ Debugging Step 3
                fetchData(selectedSession);
            }, 500);
    
            // ✅ Keep dropdown open to check if it's closing too early
            setKeepDropdownOpen(true);
        })
        .catch(error => {
            console.error("❌ Error converting column:", error);
            setMessage("❌ Failed to convert column.");
            setMessageType("error");
        });
    
        setTimeout(() => setMessage(""), 5000);
    };





    const replaceColumnValue = () => {
        if (!selectedColumnToReplace || replaceValue === undefined) {
            setMessage("⚠️ Please select a column and enter a value to replace.");
            setMessageType("warning");
            setTimeout(() => setMessage(""), 4000);
            return;
        }
    
        console.log(`🟢 Replacing "${replaceValue}" with "${newReplaceValue || ''}" in column "${selectedColumnToReplace}"...`);
    
        axios.post(`${API_URL}/api/replace_value/${selectedSession}`, { 
            column: selectedColumnToReplace, 
            find_value: replaceValue, 
            replace_with: newReplaceValue || ""  // If empty, it removes the value
        }, {
            headers: { "Content-Type": "application/json" }
        })
        .then(response => {
            console.log("✅ Backend Response:", response.data);
            setMessage(`✅ Replaced "${replaceValue}" with "${newReplaceValue || ''}" in ${selectedColumnToReplace}`);
            setMessageType("success");
    
            // ✅ Refresh data after replacement
            setTimeout(() => {
                console.log("🔄 Fetching updated dataset...");
                fetchData(selectedSession);
            }, 500);
    
            // ✅ Reset input fields
            setReplaceValue("");
            setNewReplaceValue("");
    
        })
        .catch(error => {
            console.error("❌ Error replacing value:", error);
            setMessage("❌ Failed to replace value.");
            setMessageType("error");
        });
    
        setTimeout(() => setMessage(""), 5000);
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
                                        <button className="submenu-item" onClick={detectDuplicates}>
                                            🔍 Detect Duplicates
                                        </button>
                                        <button className={`submenu-item ${showingDuplicates ? "restore-btn" : ""}`} onClick={showOnlyDuplicates}>
                                            {showingDuplicates ? "🔄 Restore All" : "📌 Show Duplicates"}
                                        </button>
                                        <button className="submenu-item red" onClick={removeDuplicates}>
                                            ❌ Remove Duplicates
                                        </button>
                                    </div>
                                )}
                            </div>

                            {/* 🔄 Convert Data Type Submenu */}
                            <div 
                                className="dropdown-item"
                                onMouseEnter={() => setShowConvertTypeMenu(true)}
                                onMouseLeave={() => setShowConvertTypeMenu(false)}
                            >
                                🔄 Convert Data Type &rsaquo;

                                {/* ✅ Column Selection Submenu */}
                                {showConvertTypeMenu && (
                                    <div 
                                        className="submenu wider-submenu" 
                                        onMouseEnter={() => setShowConvertTypeMenu(true)}
                                        onMouseLeave={() => setShowConvertTypeMenu(false)}
                                    >
                                        <label className="submenu-label">Select Column:</label>
                                        <input
                                            type="text"
                                            placeholder="Search column..."
                                            className="search-box"
                                            value={columnSearch}
                                            onChange={(e) => setColumnSearch(e.target.value)}
                                        />
                                        <select 
                                            className="column-select-box"
                                            value={selectedColumnToConvert || ""}
                                            onChange={(e) => setSelectedColumnToConvert(e.target.value)}
                                        >
                                            <option value="" disabled>Select a column</option>
                                            {columnDefs
                                                .filter(col => col.headerName.toLowerCase().includes(columnSearch.toLowerCase()))
                                                .map((col) => (
                                                    <option key={col.field} value={col.field}>
                                                        {col.headerName}
                                                    </option>
                                                ))
                                            }
                                        </select>

                                        {/* ✅ Show Data Type Selection Only If Column is Selected */}
                                        {selectedColumnToConvert && (
                                            <div className="submenu" style={{ marginTop: "10px" }}>
                                                <label className="submenu-label">Convert To:</label>
                                                <select 
                                                    className="datatype-select-box"
                                                    value={selectedDataType}
                                                    onChange={(e) => setSelectedDataType(e.target.value)}
                                                >
                                                    <option value="" disabled>Select Data Type</option>
                                                    <option value="int64">Integer</option>
                                                    <option value="float64">Float</option>
                                                    <option value="object">String</option>
                                                    <option value="boolean">Boolean</option>
                                                    <option value="datetime64">Datetime</option>
                                                    <option value="timedelta64">Timedelta</option>
                                                    <option value="date">Date</option>
                                                    <option value="time">Time</option>
                                                    <option value="currency">Currency</option>
                                                    <option value="percentage">Percentage</option>
                                                    <option value="category">Category</option>
                                                </select>

                                                {/* ✅ Show Currency Selection Only If "Currency" is Selected */}
                                                {selectedDataType === "currency" && (
                                                    <div className="submenu" style={{ marginTop: "10px" }}>
                                                        <label className="submenu-label">Select Currency:</label>
                                                        <select 
                                                            className="currency-select-box"
                                                            value={selectedCurrencySymbol}
                                                            onChange={(e) => setSelectedCurrencySymbol(e.target.value)}
                                                        >
                                                            <option value="$">USD ($)</option>
                                                            <option value="€">Euro (€)</option>
                                                            <option value="£">Pound (£)</option>
                                                            <option value="¥">Yen (¥)</option>
                                                        </select>
                                                    </div>
                                                )}

                                                {/* ✅ Apply Conversion Button */}
                                                <button 
                                                    className="apply-conversion-btn"
                                                    onClick={convertColumnDataType}
                                                >
                                                    ✅ Apply
                                                </button>
                                            </div>
                                        )}
                                    </div>
                                )}
                            </div>

                            {/* 🆕 🔄 Replace With Submenu */}
                            <div 
                                className="dropdown-item"
                                onMouseEnter={() => setShowReplaceMenu(true)}
                                onMouseLeave={() => setShowReplaceMenu(false)}
                            >
                                🔄 Replace With &rsaquo;

                                {/* ✅ Replace Submenu */}
                                {showReplaceMenu && (
                                    <div 
                                        className="submenu wider-submenu" 
                                        onMouseEnter={() => setShowReplaceMenu(true)}
                                        onMouseLeave={() => setShowReplaceMenu(false)}
                                    >
                                        <label className="submenu-label">Select Column:</label>
                                        <input
                                            type="text"
                                            placeholder="Search column..."
                                            className="search-box"
                                            value={columnSearch}
                                            onChange={(e) => setColumnSearch(e.target.value)}
                                        />
                                        <select 
                                            className="column-select-box"
                                            value={selectedColumnToReplace || ""}
                                            onChange={(e) => setSelectedColumnToReplace(e.target.value)}
                                        >
                                            <option value="" disabled>Select a column</option>
                                            {columnDefs
                                                .filter(col => col.headerName.toLowerCase().includes(columnSearch.toLowerCase()))
                                                .map((col) => (
                                                    <option key={col.field} value={col.field}>
                                                        {col.headerName}
                                                    </option>
                                                ))
                                            }
                                        </select>

                                        {/* ✅ Replacement Inputs */}
                                        {selectedColumnToReplace && (
                                            <div className="submenu" style={{ marginTop: "10px" }}>
                                                <label className="submenu-label">Find:</label>
                                                <input 
                                                    type="text" 
                                                    placeholder="Enter value to replace" 
                                                    className="replace-input"
                                                    value={replaceValue}
                                                    onChange={(e) => setReplaceValue(e.target.value)}
                                                />

                                                <label className="submenu-label">Replace With:</label>
                                                <input 
                                                    type="text" 
                                                    placeholder="Enter new value (leave empty to remove)" 
                                                    className="replace-input"
                                                    value={newReplaceValue}
                                                    onChange={(e) => setNewReplaceValue(e.target.value)}
                                                />

                                                {/* ✅ Apply Replacement Button */}
                                                <button 
                                                    className="apply-replacement-btn"
                                                    onClick={replaceColumnValue}
                                                >
                                                    ✅ Apply
                                                </button>
                                            </div>
                                        )}
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
                autoGroupColumnDef={{
                    headerName: "Group",
                    field: "group",
                    cellRenderer: "agGroupCellRenderer",
                    cellRendererParams: {
                        checkbox: true
                    }
                }}

                
                
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