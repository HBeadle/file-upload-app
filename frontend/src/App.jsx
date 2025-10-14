import React, { useState, useEffect } from "react";
import "./App.css";

const BACKEND_API_URL = import.meta.env.VITE_BACKEND_API_URL;

function App() {
    const [files, setFiles] = useState([]);
    const [dragActive, setDragActive] = useState(false);
    const [uploading, setUploading] = useState(false);
    const [message, setMessage] = useState(null);
  
    // Fetch files on mount
    useEffect(() => {
      fetchFiles();
    }, []);

    const buildApiUrl = (endpoint) => {
        const url = `${BACKEND_API_URL}/api/v1/${endpoint}`;
        console.log("Url: " + url);
        return url
    }
  
    const fetchFiles = async () => {
      try {
        const url = buildApiUrl("get_uploaded_files");
        const response = await fetch(url);
        const data = await response.json();
        setFiles(data.files);
      } catch (error) {
        setMessage({ type: "error", text: "Failed to fetch files: " + error.message });
      }
    };
  
    const uploadFile = async (file) => {
      setUploading(true);
      setMessage(null);
  
      const formData = new FormData();
      formData.append("file", file);
  
      try {
        const url = buildApiUrl("upload_file");
        const response = await fetch(url, {
          method: "POST",
          body: formData,
        });
  
        if (response.ok) {
          const data = await response.json();
          setMessage({ type: "success", text: `File "${data.filename}" uploaded successfully` });
          await fetchFiles();
        } else {
          const data = await response.json();
          setMessage({ type: "error", text: data.detail?.message || "Upload failed" });
        }
      } catch (error) {
        setMessage({ type: "error", text: "Upload failed: " + error.message });
      } finally {
        setUploading(false);
      }
    };

    const deleteFile = async (filename) => {
      try {
        const url = buildApiUrl(`delete_file/${encodeURIComponent(filename)}`);
        const response = await fetch(url, {
          method: "DELETE",
        });
    
        if (response.ok) {
          setMessage({ type: "success", text: `File "${filename}" deleted successfully` });
          await fetchFiles();
        } else {
          const data = await response.json();
          setMessage({ type: "error", text: data.detail?.message || "Delete failed" });
        }
      } catch (error) {
        setMessage({ type: "error", text: "Delete failed: " + error.message });
      }
    };
  
    const handleFileInput = (e) => {
      const file = e.target.files[0];
      if (file) {
        uploadFile(file);
      }
    };
  
    const handleDrag = (e) => {
      e.preventDefault();
      e.stopPropagation();
      if (e.type === "dragenter" || e.type === "dragover") {
        setDragActive(true);
      } else if (e.type === "dragleave") {
        setDragActive(false);
      }
    };
  
    const handleDrop = (e) => {
      e.preventDefault();
      e.stopPropagation();
      setDragActive(false);
  
      if (e.dataTransfer.files && e.dataTransfer.files[0]) {
        uploadFile(e.dataTransfer.files[0]);
      }
    };
  
    const formatBytes = (bytes) => {
      if (bytes === 0) return "0 Bytes";
      const k = 1024;
      const sizes = ["Bytes", "KB", "MB", "GB"];
      const i = Math.floor(Math.log(bytes) / Math.log(k));

      if (i >= sizes.length) {
        const gb = Math.round(bytes / Math.pow(k, 3) * 100) / 100;
        return `> ${gb} GB`;
      }
      
      return Math.round(bytes / Math.pow(k, i) * 100) / 100 + " " + sizes[i];
    };
  
    const formatDate = (isoString) => {
      return new Date(isoString).toLocaleString();
    };
  
    return (
      <div className="app">
        <div className="container">
          <h1>File Upload Service</h1>
  
          <div className="upload-section">
            <div
              className={`drop-zone ${dragActive ? "active" : ""}`}
              onDragEnter={handleDrag}
              onDragLeave={handleDrag}
              onDragOver={handleDrag}
              onDrop={handleDrop}
            >
              <p>Drag and drop a file here</p>
              <p className="or">or</p>
              <label className="file-input-label">
                Choose File
                <input
                  type="file"
                  onChange={handleFileInput}
                  disabled={uploading}
                  className="file-input"
                />
              </label>
            </div>
          </div>

          {message && (
            <div className={`message ${message.type}`}>
              {message.text}
            </div>
          )}
  
          <div className="files-section">
            <h2>Uploaded Files ({files.length})</h2>
            {files.length === 0 ? (
              <p className="no-files">No files uploaded yet</p>
            ) : (
              <table className="files-table">
                <thead>
                  <tr>
                    <th>Filename</th>
                    <th>Size</th>
                    <th>Upload Time</th>
                    <th>Delete?</th>
                  </tr>
                </thead>
                <tbody>
                  {files.map((file) => (
                    <tr key={file.filename}>
                      <td>{file.filename}</td>
                      <td>{formatBytes(file.filesize)}</td>
                      <td>{formatDate(file.upload_time)}</td>
                      <td>
                        <button 
                          onClick={() => deleteFile(file.filename)}
                          className="delete-btn"
                        >
                          Delete
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )}
          </div>
        </div>
      </div>
    );
  }
  
  export default App;