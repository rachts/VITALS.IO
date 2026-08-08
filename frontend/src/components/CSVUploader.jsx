import React, { useCallback } from 'react';
import { useDropzone } from 'react-dropzone';
import { UploadCloud } from 'lucide-react';
import { parseCSV } from '../utils/csvParser';
import { useApp } from '../context/AppContext';

const CSVUploader = () => {
  const { setRawData, setColumnMap, setFilename, setError } = useApp();

  const onDrop = useCallback((acceptedFiles) => {
    const file = acceptedFiles[0];
    if (!file) return;

    setFilename(file.name);
    setError(null);

    const reader = new FileReader();
    reader.onload = (e) => {
      try {
        const text = e.target.result;
        const { colMap, rawData } = parseCSV(text);
        setColumnMap(colMap);
        setRawData(rawData);
      } catch (err) {
        setError(err.message || "Failed to parse CSV file");
      }
    };
    reader.onerror = () => setError("Error reading file");
    reader.readAsText(file);
  }, [setColumnMap, setRawData, setError, setFilename]);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: { 'text/csv': ['.csv'] },
    maxFiles: 1
  });

  return (
    <div 
      {...getRootProps()} 
      className={`border-2 border-dashed rounded-2xl p-12 flex flex-col items-center justify-center cursor-pointer transition-all ${
        isDragActive ? 'border-accent-primary bg-accent-primary/5' : 'border-border hover:border-accent-primary/50 bg-surface'
      }`}
    >
      <input {...getInputProps()} />
      <UploadCloud className={`w-12 h-12 mb-4 transition-colors ${isDragActive ? 'text-accent-primary' : 'text-text-muted'}`} />
      <p className="text-text-primary text-lg font-medium mb-1">
        {isDragActive ? "Drop your CSV here" : "Drag & drop your CSV"}
      </p>
      <p className="text-text-muted text-sm">or click to browse files</p>
    </div>
  );
};

export default CSVUploader;
