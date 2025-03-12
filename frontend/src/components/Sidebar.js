import React, { useState } from "react";
import { NavLink } from "react-router-dom";
import { FaTable, FaChartBar, FaTools, FaBars, FaMoon, FaSun, FaChevronDown, FaChevronRight } from "react-icons/fa";
import "./Sidebar.css"; // Ensure correct import of CSS file

const Sidebar = ({ toggleTheme, theme }) => {
    const [isOpen, setIsOpen] = useState(true);
    const [isSummaryOpen, setIsSummaryOpen] = useState(false); // State for expanding/collapsing Summary Stats

    const toggleSidebar = () => {
        setIsOpen(!isOpen);
    };

    const toggleSummaryStats = () => {
        setIsSummaryOpen(!isSummaryOpen);
    };

    return (
        <div className={`sidebar ${isOpen ? "expanded" : "collapsed"} ${theme}`}>
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
                {/* Data Table */}
                <NavLink to="/" className="sidebar-link" activeClassName="active">
                    <FaTable className="icon" />
                    {isOpen && <span>Data Table</span>}
                </NavLink>

                {/* Summary Stats with expandable sub-items */}
                <div className="sidebar-item" onClick={toggleSummaryStats}>
                    <div className="sidebar-link">
                        <FaChartBar className="icon" />
                        {isOpen && <span>Summary Stats</span>}
                        {isOpen && (isSummaryOpen ? <FaChevronDown className="dropdown-icon" /> : <FaChevronRight className="dropdown-icon" />)}
                    </div>
                </div>

                {/* Sub-items under Summary Stats */}
                {isSummaryOpen && (
                    <div className="sidebar-submenu">
                        <NavLink to="/summary/descriptive" className={({ isActive }) => `sidebar-sublink ${isActive ? "active" : ""}`}>
                            <span>Descriptive Stats</span>
                        </NavLink>
                        <NavLink to="/summary/correlation" className={({ isActive }) => `sidebar-sublink ${isActive ? "active" : ""}`}>
                            <span>Correlation Matrix</span>
                        </NavLink>
                        <NavLink to="/summary/distributions" className={({ isActive }) => `sidebar-sublink ${isActive ? "active" : ""}`}>
                            <span>Distribution Analysis</span>
                        </NavLink>
                    </div>
                )}

                {/* Data Transformation */}
                <NavLink to="/transform" className="sidebar-link" activeClassName="active">
                    <FaTools className="icon" />
                    {isOpen && <span>Data Transformation</span>}
                </NavLink>
            </nav>

            {/* Theme Toggle */}
            <div className="theme-toggle">
                <button className="theme-btn" onClick={toggleTheme}>
                    {theme === "dark" ? <FaSun /> : <FaMoon />}
                    {isOpen && <span>{theme === "dark" ? " Light Mode" : " Dark Mode"}</span>}
                </button>
            </div>
        </div>
    );
};

export default Sidebar;
