import React, { useRef } from "react";

const CustomHeader = (props) => {
    const { displayName, showColumnMenu, dataType } = props;
    const buttonRef = useRef(null);

    return (
        <div 
            style={{ 
                display: "flex", 
                alignItems: "center", 
                justifyContent: "space-between", 
                width: "100%", 
                fontWeight: "bold" 
            }}
        >
            {/* ✅ Column Name with Data Type inside the header */}
            <span>
                {displayName} 
                <span 
                    style={{ 
                        fontSize: "12px", 
                        color: "#444",  // ✅ Darker gray for better visibility
                        fontWeight: "500",  // ✅ Slightly bolder
                        marginLeft: "8px",
                        backgroundColor: "#f0f0f0",  // ✅ Light gray background for contrast
                        padding: "2px 5px", 
                        borderRadius: "4px"
                    }}
                >
                    {dataType}
                </span>
            </span>

            {/* ✅ Column Menu Button */}
            <span 
                ref={buttonRef} 
                style={{ cursor: "pointer", marginLeft: "5px" }} 
                onClick={() => showColumnMenu(buttonRef.current)}
            >
                ⏷
            </span>
        </div>
    );
};

export default CustomHeader;