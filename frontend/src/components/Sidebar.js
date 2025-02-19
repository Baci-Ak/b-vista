import React, { useState } from "react";
import { NavLink } from "react-router-dom";
import { FaTable, FaChartBar, FaTools, FaBars, FaMoon, FaSun } from "react-icons/fa";
import "./Sidebar.css"; // Ensure correct import of CSS file

const Sidebar = ({ toggleTheme, darkMode }) => {
    const [isOpen, setIsOpen] = useState(true);

    const toggleSidebar = () => {
        setIsOpen(!isOpen);
    };

    return (
        <div className={`sidebar ${isOpen ? "expanded" : "collapsed"} ${darkMode ? "dark" : "light"}`}>
            <div className="sidebar-header">
                {!isOpen && <FaBars className="menu-icon" onClick={toggleSidebar} />}
                {isOpen && <h2 className="logo">🚀 B-Vista</h2>}
                {isOpen && (
                    <button className="toggle-btn" onClick={toggleSidebar}>
                        <FaBars />
                    </button>
                )}
            </div>

            <nav className="sidebar-menu">
                <NavLink to="/" className="sidebar-link" activeClassName="active">
                    <FaTable className="icon" />
                    {isOpen && <span>Data Table</span>}
                </NavLink>
                <NavLink to="/summary" className="sidebar-link" activeClassName="active">
                    <FaChartBar className="icon" />
                    {isOpen && <span>Summary Stats</span>}
                </NavLink>
                <NavLink to="/transform" className="sidebar-link" activeClassName="active">
                    <FaTools className="icon" />
                    {isOpen && <span>Data Transformation</span>}
                </NavLink>
            </nav>

            <div className="theme-toggle">
                <button className="theme-btn" onClick={toggleTheme}>
                    {darkMode ? <FaSun /> : <FaMoon />}
                    {isOpen && <span>{darkMode ? " Light Mode" : " Dark Mode"}</span>}
                </button>
            </div>
        </div>
    );
};

export default Sidebar;
