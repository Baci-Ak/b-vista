import React, { useState, useRef } from "react";

const CustomHeader = (props) => {
    const { displayName, column, showColumnMenu } = props;
    const [menuOpen, setMenuOpen] = useState(false);
    const buttonRef = useRef(null); // ✅ Create a reference for the column menu button

    // ✅ Extract column data type
    const dataType = column.colDef.dataType || "Unknown";

    return (
        <div 
            style={{ display: "flex", alignItems: "center", justifyContent: "space-between", width: "100%" }}
            onMouseEnter={() => setMenuOpen(true)}
            onMouseLeave={() => setMenuOpen(false)}
        >
            {/* ✅ Column Name */}
            <span>{displayName}</span>

            {/* ✅ Column Menu Button (Fix: Pass buttonRef.current as source) */}
            <span 
                ref={buttonRef}  // ✅ Assign ref to this element
                style={{ cursor: "pointer", marginLeft: "5px" }} 
                onClick={() => showColumnMenu(buttonRef.current)} // ✅ Pass actual DOM element, not event
            >
                ⏷
            </span>

            {/* ✅ Data Type Tooltip (Only Show on Hover) */}
            {menuOpen && (
                <div 
                    style={{
                        position: "absolute",
                        background: "#fff",
                        padding: "5px",
                        border: "1px solid #ddd",
                        borderRadius: "4px",
                        boxShadow: "0px 4px 8px rgba(0,0,0,0.1)",
                        marginTop: "5px",
                        fontSize: "12px",
                        color: "#555"
                    }}
                >
                    🛈 Data Type: <strong>{dataType}</strong>
                </div>
            )}
        </div>
    );
};

export default CustomHeader;
