import React from "react";
import { BrowserRouter as Router, Route, Routes } from "react-router-dom";  // Use Routes instead of Switch
import Layout from "./components/Layout";
import DataTable from "./pages/DataTable";
import SummaryStats from "./pages/SummaryStats";
import DescriptiveStats from "./pages/DescriptiveStats"; // ✅ Import DescriptiveStats
import CorrelationMatrix from "./pages/CorrelationMatrix"; 
import DataTransformation from "./pages/DataTransformation";
import "./App.css";


function App() {
    return (
        <Router>
            <Layout>
                <Routes>  {/* Replace Switch with Routes */}
                    <Route path="/" element={<DataTable />} />  {/* Use element={} instead of component={} */}
                    <Route path="/summary" element={<SummaryStats />} />
                    <Route path="/summary/descriptive" element={<DescriptiveStats />} />  {/* ✅ Add this */}
                    <Route path="/summary/Correlation" element={<CorrelationMatrix />} />  {/* ✅ Add this */}
                    <Route path="/transform" element={<DataTransformation />} />
                </Routes>
            </Layout>
        </Router>
    );
}

export default App;
