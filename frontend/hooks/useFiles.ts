/**
 * Custom hook for file upload and management
 */

import { useState } from "react";
import { api } from "@/lib/api";

interface FileInfo {
  id: string;
  filename: string;
  category: string;
  type: string;
  size: number;
  upload_date: string;
  status: string;
}

export function useFiles() {
  const [files, setFiles] = useState<FileInfo[]>([]);
  const [loading, setLoading] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchFiles = async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await api.files.list();
      setFiles(response.files || []);
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : "Failed to fetch files";
      setError(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  const uploadFile = async (file: File) => {
    try {
      setUploading(true);
      setError(null);
      const response = await api.files.upload(file);
      await fetchFiles(); // Refresh file list
      return response;
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : "Upload failed";
      setError(errorMessage);
      throw err;
    } finally {
      setUploading(false);
    }
  };

  const deleteFile = async (fileId: string) => {
    try {
      setError(null);
      await api.files.delete(fileId);
      await fetchFiles(); // Refresh file list
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : "Delete failed";
      setError(errorMessage);
      throw err;
    }
  };

  return {
    files,
    loading,
    uploading,
    error,
    fetchFiles,
    uploadFile,
    deleteFile,
  };
}
