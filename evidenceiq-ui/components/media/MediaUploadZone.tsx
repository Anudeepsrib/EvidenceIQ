/**
 * MediaUploadZone Component
 * react-dropzone upload panel with progress tracking.
 */

"use client";

import { useCallback, useState } from "react";
import { useDropzone } from "react-dropzone";
import { Upload, X, AlertCircle } from "lucide-react";
import { toast } from "sonner";

import { cn } from "@/lib/utils/cn";
import { formatFileSize } from "@/lib/utils/formatters";
import { useUploadMedia } from "@/lib/hooks/useMedia";
import { ALLOWED_MIME_TYPES, MAX_FILE_SIZE } from "@/lib/types/media";

interface UploadFile {
  file: File;
  id: string;
  progress: number;
  status: "pending" | "uploading" | "success" | "error";
  error?: string;
}

interface MediaUploadZoneProps {
  onClose: () => void;
}

export function MediaUploadZone({ onClose }: MediaUploadZoneProps) {
  const [files, setFiles] = useState<UploadFile[]>([]);
  const uploadMutation = useUploadMedia();

  const onDrop = useCallback((acceptedFiles: File[], rejectedFiles: any[]) => {
    // Handle rejected files
    rejectedFiles.forEach(({ file, errors }) => {
      const errorMsg = errors.map((e: any) => e.message).join(", ");
      toast.error(`${file.name}: ${errorMsg}`);
    });

    // Add accepted files
    const newFiles: UploadFile[] = acceptedFiles.map((file) => ({
      file,
      id: `${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
      progress: 0,
      status: "pending",
    }));

    setFiles((prev) => [...prev, ...newFiles]);

    // Start uploads
    newFiles.forEach((uploadFile) => {
      handleUpload(uploadFile);
    });
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      "image/*": [".jpeg", ".jpg", ".png", ".tiff", ".webp"],
      "video/*": [".mp4", ".mov", ".avi"],
      "application/pdf": [".pdf"],
    },
    maxSize: MAX_FILE_SIZE,
    multiple: true,
  });

  const handleUpload = async (uploadFile: UploadFile) => {
    setFiles((prev) =>
      prev.map((f) =>
        f.id === uploadFile.id ? { ...f, status: "uploading" } : f
      )
    );

    uploadMutation.mutate(
      {
        file: uploadFile.file,
        onProgress: (progress) => {
          setFiles((prev) =>
            prev.map((f) =>
              f.id === uploadFile.id ? { ...f, progress } : f
            )
          );
        },
      },
      {
        onSuccess: () => {
          setFiles((prev) =>
            prev.map((f) =>
              f.id === uploadFile.id ? { ...f, status: "success", progress: 100 } : f
            )
          );
        },
        onError: (error: Error) => {
          setFiles((prev) =>
            prev.map((f) =>
              f.id === uploadFile.id
                ? { ...f, status: "error", error: error.message }
                : f
            )
          );
        },
      }
    );
  };

  const removeFile = (id: string) => {
    setFiles((prev) => prev.filter((f) => f.id !== id));
  };

  return (
    <div className="bg-surface border border-border rounded-lg p-6 mb-6">
      <div className="flex items-center justify-between mb-4">
        <h3 className="font-medium text-text-primary">Upload Media</h3>
        <button
          onClick={onClose}
          className="p-1 text-text-tertiary hover:text-text-secondary"
        >
          <X className="w-5 h-5" />
        </button>
      </div>

      {/* Dropzone */}
      <div
        {...getRootProps()}
        className={cn(
          "border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-colors",
          isDragActive
            ? "border-accent bg-accent-muted"
            : "border-border hover:border-border-strong"
        )}
      >
        <input {...getInputProps()} />
        <Upload className="w-8 h-8 text-text-secondary mx-auto mb-3" />
        <p className="text-text-primary font-medium">
          {isDragActive ? "Drop files here" : "Drag & drop files here"}
        </p>
        <p className="text-text-secondary text-sm mt-1">
          or click to select files
        </p>
        <p className="text-text-tertiary text-xs mt-2">
          JPEG, PNG, TIFF, WEBP, MP4, MOV, AVI, PDF (max 500MB)
        </p>
      </div>

      {/* File list */}
      {files.length > 0 && (
        <div className="mt-4 space-y-3">
          {files.map((file) => (
            <div
              key={file.id}
              className="flex items-center gap-3 p-3 bg-surface-raised rounded-md"
            >
              {/* File icon */}
              <div className="w-10 h-10 bg-surface rounded flex items-center justify-center flex-shrink-0">
                <Upload className="w-5 h-5 text-text-secondary" />
              </div>

              {/* File info */}
              <div className="flex-1 min-w-0">
                <p className="text-sm text-text-primary truncate">
                  {file.file.name}
                </p>
                <p className="text-xs text-text-tertiary">
                  {formatFileSize(file.file.size)}
                </p>

                {/* Progress bar */}
                {file.status === "uploading" && (
                  <div className="mt-2">
                    <div className="h-1 bg-border rounded-full overflow-hidden">
                      <div
                        className="h-full bg-accent transition-all duration-300"
                        style={{ width: `${file.progress}%` }}
                      />
                    </div>
                    <p className="text-xs text-text-secondary mt-1">
                      {file.progress}%
                    </p>
                  </div>
                )}

                {/* Error message */}
                {file.status === "error" && (
                  <div className="flex items-center gap-1 mt-1 text-error text-xs">
                    <AlertCircle className="w-3 h-3" />
                    <span>{file.error || "Upload failed"}</span>
                  </div>
                )}

                {/* Success indicator */}
                {file.status === "success" && (
                  <p className="text-xs text-success mt-1">Upload complete</p>
                )}
              </div>

              {/* Remove button */}
              <button
                onClick={() => removeFile(file.id)}
                className="p-1 text-text-tertiary hover:text-error"
              >
                <X className="w-4 h-4" />
              </button>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
