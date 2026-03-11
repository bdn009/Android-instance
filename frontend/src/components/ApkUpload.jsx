import { useCallback, useState } from 'react';
import { useDropzone } from 'react-dropzone';
import { Upload, FileBox, Loader2, Check } from 'lucide-react';
import api from '../services/api';
import toast from 'react-hot-toast';

export default function ApkUpload({ onUploaded }) {
    const [uploading, setUploading] = useState(false);
    const [uploadedFile, setUploadedFile] = useState(null);

    const onDrop = useCallback(async (acceptedFiles) => {
        const file = acceptedFiles[0];
        if (!file) return;

        if (!file.name.endsWith('.apk')) {
            toast.error('Only .apk files are allowed');
            return;
        }

        setUploading(true);
        const formData = new FormData();
        formData.append('file', file);

        try {
            const { data } = await api.post('/apk/upload', formData, {
                headers: { 'Content-Type': 'multipart/form-data' },
            });
            setUploadedFile(data);
            toast.success(`${file.name} uploaded successfully`);
            if (onUploaded) onUploaded(data);
        } catch (err) {
            toast.error(err.response?.data?.detail || 'Upload failed');
        }
        setUploading(false);
    }, [onUploaded]);

    const { getRootProps, getInputProps, isDragActive } = useDropzone({
        onDrop,
        accept: { 'application/vnd.android.package-archive': ['.apk'] },
        maxFiles: 1,
        disabled: uploading,
    });

    return (
        <div
            {...getRootProps()}
            className={`relative rounded-2xl border-2 border-dashed p-8 text-center cursor-pointer transition-all duration-300
        ${isDragActive
                    ? 'border-primary-400 bg-primary-500/10'
                    : 'border-surface-600/40 hover:border-surface-500/60 bg-surface-800/30'
                }
        ${uploading ? 'pointer-events-none opacity-60' : ''}
      `}
        >
            <input {...getInputProps()} />

            {uploading ? (
                <div className="flex flex-col items-center gap-3">
                    <Loader2 className="w-10 h-10 text-primary-400 animate-spin" />
                    <p className="text-sm text-surface-300">Uploading APK...</p>
                </div>
            ) : uploadedFile ? (
                <div className="flex flex-col items-center gap-3">
                    <div className="w-12 h-12 rounded-xl bg-green-500/15 flex items-center justify-center">
                        <Check className="w-6 h-6 text-green-400" />
                    </div>
                    <div>
                        <p className="text-sm font-medium text-white">{uploadedFile.name}</p>
                        <p className="text-xs text-surface-400 mt-1">Uploaded successfully • Drop another to replace</p>
                    </div>
                </div>
            ) : (
                <div className="flex flex-col items-center gap-3">
                    <div className="w-12 h-12 rounded-xl bg-surface-700/50 flex items-center justify-center group-hover:bg-surface-700/80 transition-colors">
                        {isDragActive ? (
                            <FileBox className="w-6 h-6 text-primary-400" />
                        ) : (
                            <Upload className="w-6 h-6 text-surface-400" />
                        )}
                    </div>
                    <div>
                        <p className="text-sm font-medium text-surface-300">
                            {isDragActive ? 'Drop APK here' : 'Drag & drop an APK file'}
                        </p>
                        <p className="text-xs text-surface-500 mt-1">or click to browse • .apk files only</p>
                    </div>
                </div>
            )}
        </div>
    );
}
