import React, { useState, useRef } from 'react';
import { UploadCloud, FileSpreadsheet, CheckCircle2, AlertCircle, Loader2 } from 'lucide-react';
import { pandasApi } from '../../api/pandasApi';
import { chatApi } from '../../api/chatApi';
import { useNavigate } from 'react-router-dom';
import { Button } from '../ui/button';

interface CsvUploaderProps {
  onUploadSuccess?: (filePath: string) => void;
}

export const CsvUploader: React.FC<CsvUploaderProps> = ({ onUploadSuccess }) => {
  const [file, setFile] = useState<File | null>(null);
  const [isUploading, setIsUploading] = useState<boolean>(false);
  const [progress, setProgress] = useState<number>(0);
  const [isDragOver, setIsDragOver] = useState<boolean>(false);
  const [status, setStatus] = useState<{
    type: 'success' | 'error' | null;
    message: string;
  }>({ type: null, message: '' });

  const fileInputRef = useRef<HTMLInputElement>(null);
  const navigate = useNavigate();

  const handleFileSelect = (selectedFile: File) => {
    if (!selectedFile.name.endsWith('.csv')) {
      setStatus({
        type: 'error',
        message: 'Invalid file type. Only CSV files are supported.',
      });
      return;
    }
    setFile(selectedFile);
    setStatus({ type: null, message: '' });
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFileSelect(e.dataTransfer.files[0]);
    }
  };

  const handleUpload = async () => {
    if (!file) return;
    setIsUploading(true);
    setProgress(30);
    setStatus({ type: null, message: '' });

    try {
      const res = await pandasApi.uploadCsv(file);
      setProgress(100);
      setStatus({
        type: 'success',
        message: res.message || `CSV "${file.name}" uploaded successfully!`,
      });

      if (onUploadSuccess) {
        onUploadSuccess(res.file_path);
      }

      // Automatically create a new Pandas Chat Session using the uploaded CSV path
      const session = await chatApi.createSession({
        agent_type: 'pandas',
        title: res.file_path, // Store the CSV file path in title for Pandas agent
      });

      setTimeout(() => {
        navigate(`/chat/${session.id}`);
      }, 1000);
    } catch (err: any) {
      const errMsg =
        err?.response?.data?.detail || err?.message || 'Failed to upload CSV file.';
      setStatus({ type: 'error', message: errMsg });
    } finally {
      setIsUploading(false);
    }
  };

  return (
    <div className="w-full space-y-4">
      <div
        onDragOver={(e) => {
          e.preventDefault();
          setIsDragOver(true);
        }}
        onDragLeave={() => setIsDragOver(false)}
        onDrop={handleDrop}
        onClick={() => fileInputRef.current?.click()}
        className={`relative flex flex-col items-center justify-center p-10 rounded-2xl border-2 border-dashed transition-all duration-300 cursor-pointer ${
          isDragOver
            ? 'border-cyan-400 bg-cyan-500/10 scale-[1.01] shadow-lg shadow-cyan-500/10'
            : file
            ? 'border-emerald-500/40 bg-emerald-500/5'
            : 'border-white/[0.08] hover:border-cyan-500/40 bg-space-surface/60 hover:bg-space-surface/90'
        }`}
      >
        <input
          ref={fileInputRef}
          type="file"
          accept=".csv"
          onChange={(e) => e.target.files?.[0] && handleFileSelect(e.target.files[0])}
          className="hidden"
        />

        <div className="w-14 h-14 rounded-2xl bg-cyan-500/10 border border-cyan-500/25 flex items-center justify-center text-cyan-400 mb-4 shadow-lg shadow-cyan-500/10">
          <FileSpreadsheet className="w-7 h-7" />
        </div>

        {file ? (
          <div className="text-center space-y-1">
            <p className="text-sm font-bold text-emerald-300 font-mono">{file.name}</p>
            <p className="text-xs text-slate-400">
              Size: {(file.size / (1024 * 1024)).toFixed(2)} MB • Ready to analyze
            </p>
          </div>
        ) : (
          <div className="text-center space-y-1">
            <p className="text-sm font-semibold text-slate-200 font-heading">
              Drag & Drop your CSV dataset here, or <span className="text-cyan-400 underline">Browse</span>
            </p>
            <p className="text-xs text-slate-500">Supports .csv files up to 100MB</p>
          </div>
        )}
      </div>

      {/* Progress Bar */}
      {isUploading && (
        <div className="w-full space-y-1.5 animate-fade-in-up">
          <div className="flex justify-between text-xs text-slate-400 font-mono">
            <span>Uploading dataset to Pandas Agent...</span>
            <span>{progress}%</span>
          </div>
          <div className="w-full h-2 bg-space-elevated rounded-full overflow-hidden">
            <div
              className="h-full bg-gradient-to-r from-violet-500 via-cyan-400 to-emerald-400 transition-all duration-300"
              style={{ width: `${progress}%` }}
            />
          </div>
        </div>
      )}

      {/* Status Messages */}
      {status.type === 'success' && (
        <div className="p-4 rounded-xl bg-emerald-500/10 border border-emerald-500/25 text-emerald-300 text-xs flex items-center gap-3 animate-fade-in-up">
          <CheckCircle2 className="w-5 h-5 text-emerald-400 shrink-0" />
          <span>{status.message} Redirecting to Chat Workspace...</span>
        </div>
      )}

      {status.type === 'error' && (
        <div className="p-4 rounded-xl bg-rose-500/10 border border-rose-500/25 text-rose-300 text-xs flex items-center gap-3 animate-fade-in-up">
          <AlertCircle className="w-4 h-4 text-rose-400 shrink-0" />
          <span>{status.message}</span>
        </div>
      )}

      {/* Upload Button */}
      {file && (
        <div className="flex justify-end">
          <Button
            onClick={handleUpload}
            isLoading={isUploading}
            leftIcon={<UploadCloud className="w-4 h-4" />}
          >
            Upload & Launch Pandas Chat
          </Button>
        </div>
      )}
    </div>
  );
};
