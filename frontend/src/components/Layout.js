import React, { useState } from "react";
import Sidebar from "./Sidebar";
import "./Layout.css"; // Make sure you have this file created

const Layout = ({ children }) => {
    const [darkMode, setDarkMode] = useState(false);

    const toggleTheme = () => {
        setDarkMode(!darkMode);
        document.body.classList.toggle("dark-mode", !darkMode);
    };

    return (
        <div className={`layout ${darkMode ? "dark" : "light"}`}>
            <Sidebar toggleTheme={toggleTheme} darkMode={darkMode} />
            <main className="content">{children}</main>
        </div>
    );
};

export default Layout;
