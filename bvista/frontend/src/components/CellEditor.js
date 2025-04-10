import React, { useEffect, useRef, useState, forwardRef } from "react";

const CellEditor = forwardRef((props, ref) => {
    const [value, setValue] = useState(props.value);
    const inputRef = useRef(null);

    // Focus input when the editor is opened
    useEffect(() => {
        setTimeout(() => {
            if (inputRef.current) {
                inputRef.current.focus();
                inputRef.current.select(); // Select text for easy editing
            }
        }, 50);
    }, []);

    // Make sure getValue() returns the correct updated value
    useEffect(() => {
        if (ref) {
            ref.current = {
                getValue: () => value, // ✅ Ensures Ag-Grid gets the updated value
            };
        }
    }, [value, ref]);

    return (
        <input
            ref={inputRef}
            type="text"
            value={value}
            onChange={(e) => setValue(e.target.value)}
            onKeyDown={(e) => {
                if (e.key === "Enter") {
                    props.stopEditing(); // ✅ Save on Enter
                } else if (e.key === "Escape") {
                    props.stopEditing(true); // ✅ Cancel on Escape
                }
            }}
            style={{
                width: "100%",
                height: "100%",
                border: "none",
                outline: "none",
                padding: "5px",
                fontSize: "14px",
                background: "white",
            }}
        />
    );
});

export default CellEditor;
