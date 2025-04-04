import React, { useState } from "react";
import { NavLink } from "react-router-dom";
import { FaTable, FaChartBar, FaTools, FaBars, FaMoon, FaSun, FaChevronDown, FaChevronRight } from "react-icons/fa";
import "./Sidebar.css"; // Ensure correct import of CSS file

const Sidebar = ({ toggleTheme, theme }) => {
    const [isOpen, setIsOpen] = useState(true);
    const [isSummaryOpen, setIsSummaryOpen] = useState(false); // State for Summary Stats
    const [isMissingOpen, setIsMissingOpen] = useState(false); // State for Missing Values

    const toggleSidebar = () => {
        setIsOpen(!isOpen);
    };

    const toggleSummaryStats = () => {
        setIsSummaryOpen(!isSummaryOpen);
        setIsMissingOpen(false); // Ensure Missing Values collapses when Summary Stats expands
    };

    const toggleMissingValues = () => {
        setIsMissingOpen(!isMissingOpen);
        setIsSummaryOpen(false); // Ensure Summary Stats collapses when Missing Values expands
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
                <NavLink to="/" className="sidebar-link">
                    <FaTable className="icon" />
                    {isOpen && <span>Data Table</span>}
                </NavLink>

                {/* Summary Stats (Expandable) */}
                <div className="sidebar-item" onClick={toggleSummaryStats}>
                    <div className="sidebar-link">
                        <FaChartBar className="icon" />
                        {isOpen && <span>Summary Stats</span>}
                        {isOpen && (isSummaryOpen ? <FaChevronDown className="dropdown-icon" /> : <FaChevronRight className="dropdown-icon" />)}
                    </div>
                </div>

                {/* Submenu for Summary Stats */}
                {isSummaryOpen && (
                    <div className="sidebar-submenu">
                        <NavLink to="/summary/descriptive" className="sidebar-sublink">
                            <span>Descriptive Stats</span>
                        </NavLink>
                        <NavLink to="/summary/correlation" className="sidebar-sublink">
                            <span>Correlation Matrix</span>
                        </NavLink>
                        <NavLink to="/summary/distributions" className="sidebar-sublink">
                            <span>Distribution Analysis</span>
                        </NavLink>
                    </div>
                )}

                {/* Missing Values (Expandable) */}
                <div className="sidebar-item" onClick={toggleMissingValues}>
                    <div className="sidebar-link">
                        <FaChartBar className="icon" />
                        {isOpen && <span>Missing Values</span>}
                        {isOpen && (isMissingOpen ? <FaChevronDown className="dropdown-icon" /> : <FaChevronRight className="dropdown-icon" />)}
                    </div>
                </div>

                {/* Submenu for Missing Values */}
                {isMissingOpen && (
                    <div className="sidebar-submenu">
                        <NavLink to="/Missing/MissingDataAnalysis" className="sidebar-sublink">
                            <span>Missing Data Analysis</span>
                        </NavLink>
                        <NavLink to="/Missing/MissingDataDiagnostics" className="sidebar-sublink">
                            <span>Missing Data Diagnostics</span>
                        </NavLink>
                        <NavLink to="/Missing/DataCleaning" className="sidebar-sublink">
                            <span>Data Cleaning</span>
                        </NavLink>
                    </div>
                )}

                {/* Data Transformation */}
                <NavLink to="/transform" className="sidebar-link">
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
