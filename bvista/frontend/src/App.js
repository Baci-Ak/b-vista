import React from "react";
import { BrowserRouter as Router, Route, Routes } from "react-router-dom";  // Use Routes instead of Switch
import Layout from "./components/Layout";
import DataTable from "./pages/DataTable";
import SummaryStats from "./pages/SummaryStats";
import DescriptiveStats from "./pages/DescriptiveStats";
import CorrelationMatrix from "./pages/CorrelationMatrix";
import DataTransformation from "./pages/DataTransformation";
import DistributionAnalysis from "./pages/DistributionAnalysis";

import MissingValues from "./pages/MissingValues";
import MissingDataAnalysis from "./pages/MissingDataAnalysis";  // ✅ Fixed naming
import MissingDataDiagnostics from "./pages/MissingDataDiagnostics";  // ✅ Fixed naming
import DataCleaning from "./pages/DataCleaning";

import "./App.css";

function App() {
    return (
        <Router>
            <Layout>
                <Routes>  
                    <Route path="/" element={<DataTable />} />
                    <Route path="/summary" element={<SummaryStats />} />
                    <Route path="/summary/descriptive" element={<DescriptiveStats />} />
                    <Route path="/summary/correlation" element={<CorrelationMatrix />} />  {/* ✅ Fixed route */}
                    <Route path="/summary/distributions" element={<DistributionAnalysis />} />
                    
                    <Route path="/missing" element={<MissingValues />} />
                    <Route path="/missing/MissingDataAnalysis" element={<MissingDataAnalysis />} />  {/* ✅ Fixed naming */}
                    <Route path="/missing/MissingDataDiagnostics" element={<MissingDataDiagnostics />} />  {/* ✅ Fixed naming */}
                    <Route path="/missing/dataCleaning" element={<DataCleaning />} />  {/* ✅ Fixed case */}
                    
                    <Route path="/transform" element={<DataTransformation />} />
                </Routes>
            </Layout>
        </Router>
    );
}

export default App;
