import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { UploadCloud, CheckCircle, XCircle, AlertTriangle, FileText, Database, Plane } from 'lucide-react';

// Use standard API URL for local dev, and Vercel will handle '/api' relative path in production
const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';

function App() {
  const [records, setRecords] = useState([]);
  const [loading, setLoading] = useState(true);
  const [uploadFile, setUploadFile] = useState(null);
  const [uploadSource, setUploadSource] = useState('SAP');
  const [uploading, setUploading] = useState(false);
  const [filter, setFilter] = useState('ALL');

  const totalRecords = records.length;
  const approvedRecords = records.filter(r => r.status === 'APPROVED').length;
  const pendingRecords = records.filter(r => r.status === 'PENDING' || r.status === 'FLAGGED').length;

  const filteredRecords = records.filter(r => {
    if (filter === 'ALL') return true;
    if (filter === 'NEEDS_REVIEW') return r.status === 'PENDING' || r.status === 'FLAGGED';
    if (filter === 'APPROVED') return r.status === 'APPROVED';
    return true;
  });

  useEffect(() => {
    // Initial data setup if empty, then fetch
    axios.post(`${API_URL}/setup/`).then(() => {
      fetchRecords();
    }).catch(err => {
      console.error("Setup error", err);
      fetchRecords();
    });
  }, []);

  const fetchRecords = async () => {
    setLoading(true);
    try {
      const res = await axios.get(`${API_URL}/records/`);
      setRecords(res.data);
    } catch (error) {
      console.error("Error fetching records:", error);
    } finally {
      setLoading(false);
    }
  };

  const handleUpload = async (e) => {
    e.preventDefault();
    if (!uploadFile) return;
    
    setUploading(true);
    const formData = new FormData();
    formData.append('file', uploadFile);
    formData.append('source', uploadSource);

    try {
      await axios.post(`${API_URL}/upload/`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });
      fetchRecords();
      setUploadFile(null);
    } catch (error) {
      console.error("Upload error", error);
      alert(error.response?.data?.error || "Failed to upload file.");
    } finally {
      setUploading(false);
    }
  };

  const updateStatus = async (id, status) => {
    try {
      await axios.patch(`${API_URL}/records/${id}/`, { status });
      fetchRecords();
    } catch (error) {
      console.error("Update error", error);
    }
  };

  const clearData = async (sourceOnly = false) => {
    if (!window.confirm("Are you sure you want to clear the data?")) return;
    try {
      setUploading(true);
      const payload = sourceOnly ? { source: uploadSource } : {};
      await axios.post(`${API_URL}/clear/`, payload);
      fetchRecords();
    } catch (error) {
      console.error("Clear error", error);
      alert("Failed to clear data.");
    } finally {
      setUploading(false);
    }
  };

  const getStatusIcon = (status) => {
    switch(status) {
      case 'APPROVED': return <CheckCircle className="text-green-500 w-5 h-5" />;
      case 'REJECTED': return <XCircle className="text-red-500 w-5 h-5" />;
      case 'FLAGGED': return <AlertTriangle className="text-yellow-500 w-5 h-5" />;
      default: return <FileText className="text-gray-400 w-5 h-5" />;
    }
  };

  const getSourceIcon = (sourceName) => {
    if (!sourceName) return <Database className="text-gray-400 w-5 h-5" />;
    if (sourceName.toLowerCase().includes('sap')) return <Database className="text-blue-500 w-5 h-5" />;
    if (sourceName.toLowerCase().includes('travel')) return <Plane className="text-purple-500 w-5 h-5" />;
    return <FileText className="text-green-500 w-5 h-5" />;
  };

  return (
    <div className="min-h-screen bg-gray-50 text-gray-900 font-sans">
      {/* Header */}
      <header className="bg-white border-b border-gray-200 sticky top-0 z-10">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4 flex justify-between items-center">
          <div className="flex items-center space-x-3">
            <div className="w-9 h-9 bg-blue-600 rounded-lg flex items-center justify-center shadow-sm">
              <Database className="text-white w-5 h-5" />
            </div>
            <h1 className="text-xl font-bold text-gray-900 tracking-tight">
              Breathe <span className="font-medium text-gray-500">Data Hub</span>
            </h1>
          </div>
          <div className="flex space-x-3">
            <button 
              onClick={() => clearData(true)} 
              disabled={uploading}
              className="px-4 py-2 text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 rounded-md border border-gray-300 transition-colors disabled:opacity-50"
            >
              Clear Category
            </button>
            <button 
              onClick={() => clearData(false)} 
              disabled={uploading}
              className="px-4 py-2 text-sm font-medium text-red-600 bg-white hover:bg-red-50 rounded-md border border-red-200 transition-colors disabled:opacity-50"
            >
              Clear Database
            </button>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
        
        {/* Metric Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          <div className="bg-white border border-gray-200 rounded-xl p-6 shadow-sm flex flex-col items-center">
            <span className="text-gray-500 text-xs uppercase tracking-wider font-semibold">Total Records</span>
            <span className="text-3xl font-bold text-gray-900 mt-2">{totalRecords}</span>
          </div>
          <div className="bg-white border border-gray-200 rounded-xl p-6 shadow-sm flex flex-col items-center">
            <span className="text-yellow-600 text-xs uppercase tracking-wider font-semibold">Needs Review</span>
            <span className="text-3xl font-bold text-yellow-600 mt-2">{pendingRecords}</span>
          </div>
          <div className="bg-white border border-gray-200 rounded-xl p-6 shadow-sm flex flex-col items-center">
            <span className="text-green-600 text-xs uppercase tracking-wider font-semibold">Approved</span>
            <span className="text-3xl font-bold text-green-600 mt-2">{approvedRecords}</span>
          </div>
        </div>

        {/* Upload Section */}
        <section className="bg-white rounded-xl p-6 border border-gray-200 shadow-sm">
          <h2 className="text-lg font-semibold text-gray-900 mb-4 flex items-center space-x-2">
            <UploadCloud className="w-5 h-5 text-blue-600" />
            <span>Data Ingestion</span>
          </h2>
          <form onSubmit={handleUpload} className="flex flex-col sm:flex-row gap-4 items-end">
            <div className="flex-1 w-full">
              <label className="block text-sm font-medium text-gray-700 mb-1">Data Source</label>
              <select 
                value={uploadSource} 
                onChange={(e) => setUploadSource(e.target.value)}
                className="w-full bg-white border border-gray-300 rounded-md px-3 py-2 text-sm text-gray-900 focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition-all shadow-sm"
              >
                <option value="SAP">SAP (Fuel & Procurement)</option>
                <option value="Utility">Utility Portal (Electricity)</option>
                <option value="Travel">Corporate Travel (Flights)</option>
              </select>
            </div>
            <div className="flex-1 w-full">
              <label className="block text-sm font-medium text-gray-700 mb-1">Upload CSV</label>
              <input 
                type="file" 
                accept=".csv"
                onChange={(e) => setUploadFile(e.target.files[0])}
                className="w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-md file:border-0 file:text-sm file:font-medium file:bg-blue-50 file:text-blue-600 hover:file:bg-blue-100 transition-all cursor-pointer bg-white border border-gray-300 rounded-md shadow-sm"
              />
            </div>
            <button 
              type="submit" 
              disabled={!uploadFile || uploading}
              className="w-full sm:w-auto px-6 py-2.5 bg-blue-600 hover:bg-blue-700 text-white text-sm font-medium rounded-md shadow-sm transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center space-x-2"
            >
              {uploading ? <span className="animate-pulse">Processing...</span> : <span>Upload</span>}
            </button>
          </form>
        </section>

        {/* Dashboard Section */}
        <section className="bg-white rounded-xl border border-gray-200 shadow-sm overflow-hidden">
          <div className="px-6 py-4 border-b border-gray-200 flex flex-col sm:flex-row justify-between items-center gap-4 bg-gray-50">
            <div className="flex items-center space-x-2">
              <h2 className="text-lg font-semibold text-gray-900">Review Queue</h2>
            </div>
            
            {/* Filters */}
            <div className="flex space-x-1 bg-gray-200 p-1 rounded-md">
              <button 
                onClick={() => setFilter('ALL')}
                className={`px-3 py-1 rounded text-sm font-medium transition-colors ${filter === 'ALL' ? 'bg-white text-gray-900 shadow-sm' : 'text-gray-600 hover:text-gray-900'}`}
              >
                All
              </button>
              <button 
                onClick={() => setFilter('NEEDS_REVIEW')}
                className={`px-3 py-1 rounded text-sm font-medium transition-colors ${filter === 'NEEDS_REVIEW' ? 'bg-white text-yellow-700 shadow-sm' : 'text-gray-600 hover:text-gray-900'}`}
              >
                Needs Review
              </button>
              <button 
                onClick={() => setFilter('APPROVED')}
                className={`px-3 py-1 rounded text-sm font-medium transition-colors ${filter === 'APPROVED' ? 'bg-white text-green-700 shadow-sm' : 'text-gray-600 hover:text-gray-900'}`}
              >
                Approved
              </button>
            </div>
          </div>
          
          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm whitespace-nowrap">
              <thead className="bg-white text-gray-500 font-medium text-xs uppercase tracking-wider border-b border-gray-200">
                <tr>
                  <th className="px-6 py-3 font-semibold">Status</th>
                  <th className="px-6 py-3 font-semibold">Source</th>
                  <th className="px-6 py-3 font-semibold">Category</th>
                  <th className="px-6 py-3 font-semibold">Activity</th>
                  <th className="px-6 py-3 font-semibold">Normalized Value</th>
                  <th className="px-6 py-3 font-semibold">Issues</th>
                  <th className="px-6 py-3 font-semibold">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-200 bg-white">
                {loading ? (
                  <tr>
                    <td colSpan="7" className="px-6 py-8 text-center text-gray-500 animate-pulse">Loading records...</td>
                  </tr>
                ) : filteredRecords.length === 0 ? (
                  <tr>
                    <td colSpan="7" className="px-6 py-8 text-center text-gray-500">No records match this filter.</td>
                  </tr>
                ) : (
                  filteredRecords.map((record) => (
                    <tr key={record.id} className="hover:bg-gray-50 transition-colors group">
                      <td className="px-6 py-4">
                        <div className="flex items-center space-x-2">
                          {getStatusIcon(record.status)}
                          <span className={`font-medium ${
                            record.status === 'APPROVED' ? 'text-green-600' :
                            record.status === 'REJECTED' ? 'text-red-600' :
                            record.status === 'FLAGGED' ? 'text-yellow-600' : 'text-gray-500'
                          }`}>{record.status}</span>
                        </div>
                      </td>
                      <td className="px-6 py-4">
                        <div className="flex items-center space-x-2">
                          {getSourceIcon(record.source_name)}
                          <span className="text-gray-900 font-medium">{record.source_name}</span>
                        </div>
                      </td>
                      <td className="px-6 py-4">
                        <span className="px-2.5 py-1 bg-gray-100 text-gray-600 rounded-md text-xs font-medium border border-gray-200">{record.scope_category}</span>
                      </td>
                      <td className="px-6 py-4 text-gray-600">{record.activity_type}</td>
                      <td className="px-6 py-4 font-mono text-gray-900">
                        {record.normalized_value !== null ? `${record.normalized_value.toFixed(2)} ${record.normalized_unit}` : 'N/A'}
                        {record.original_value !== null && (
                          <div className="text-xs text-gray-500 mt-1 font-sans">Orig: {record.original_value} {record.original_unit}</div>
                        )}
                      </td>
                      <td className="px-6 py-4">
                        {Object.keys(record.issues).length > 0 ? (
                          <div className="flex flex-col space-y-1">
                            {Object.entries(record.issues).map(([k, v]) => (
                              <span key={k} className="text-xs bg-yellow-50 text-yellow-800 px-2 py-1 rounded border border-yellow-200">{v}</span>
                            ))}
                          </div>
                        ) : <span className="text-gray-400 text-xs italic">None</span>}
                      </td>
                      <td className="px-6 py-4">
                        <div className="flex space-x-2 opacity-0 group-hover:opacity-100 transition-opacity">
                          {record.status !== 'APPROVED' && (
                            <button onClick={() => updateStatus(record.id, 'APPROVED')} className="p-1 text-gray-400 hover:text-green-600 hover:bg-green-50 rounded transition-colors" title="Approve">
                              <CheckCircle className="w-5 h-5" />
                            </button>
                          )}
                          {record.status !== 'REJECTED' && (
                            <button onClick={() => updateStatus(record.id, 'REJECTED')} className="p-1 text-gray-400 hover:text-red-600 hover:bg-red-50 rounded transition-colors" title="Reject">
                              <XCircle className="w-5 h-5" />
                            </button>
                          )}
                        </div>
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </section>
      </main>
    </div>
  );
}

export default App;
