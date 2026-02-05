/**
 * Document Upload component - allows users to upload PDF/TXT files.
 * 
 * Best practices applied:
 * - Uses SWR Mutation for file uploads (client-swr-dedup)
 * - React.memo to prevent unnecessary re-renders
 * - Direct imports from antd submodules (bundle-barrel-imports)
 * - useCallback for stable function references
 * - Event handler contains interaction logic (rerender-move-effect-to-event)
 * - Lazy state initialization if needed (rerender-lazy-state-init)
 */

import { memo, useCallback, useRef } from 'react';
import Card from 'antd/es/card';
import Button from 'antd/es/button';
import Upload from 'antd/es/upload';
import Tag from 'antd/es/tag';
import type { UploadFile } from 'antd/es/upload';
import message from 'antd/es/message';
import { InboxOutlined } from '@ant-design/icons';
import { useUploadDocument } from '../hooks/useApi';

// Memoized component for performance
export const DocumentUpload = memo(function DocumentUpload() {
  const { trigger: uploadFile, isMutating: isLoading } = useUploadDocument();
  
  // Use ref to track if we should process the upload
  const isProcessingRef = useRef(false);

  // Stable callback for upload handling
  const handleUpload = useCallback(async (info: { file: UploadFile; fileList: UploadFile[] }) => {
    // Prevent duplicate processing
    if (isProcessingRef.current) return;
    
    const file = info.file.originFileObj || info.file;
    if (!file || !(file instanceof File)) return;

    isProcessingRef.current = true;

    try {
      const result = await uploadFile(file);

      if (result.success) {
        message.success(
          `Document uploaded successfully! File: ${result.filename}, Chunks: ${result.chunks_created}`,
          4
        );

        // Dispatch event to refresh stats
        window.dispatchEvent(new CustomEvent('documentUploaded'));
      } else {
        message.error(result.message || 'Upload failed');
      }
    } catch (error) {
      console.error('Upload error:', error);
      message.error('Failed to upload document. Please try again.');
    } finally {
      isProcessingRef.current = false;
    }
  }, [uploadFile]);

  return (
    <Card
      title={
        <span style={{ fontSize: '15px', fontWeight: 600, color: '#262626' }}>
          Upload Document
        </span>
      }
      extra={
        <Upload
          accept=".pdf,.txt"
          onChange={handleUpload}
          beforeUpload={() => false}
          showUploadList={false}
          disabled={isLoading}
          multiple={false}
        >
          <Button 
            icon={<InboxOutlined />} 
            loading={isLoading}
            type="default"
            style={{ 
              color: '#dc143c',
              borderColor: '#dc143c'
            }}
          >
            {isLoading ? 'Uploading...' : 'Select File'}
          </Button>
        </Upload>
      }
      style={{ 
        background: '#ffffff',
        border: '1px solid #e8e8e8'
      }}
      bodyStyle={{ padding: '16px' }}
    >
      <div style={{ textAlign: 'center', padding: '8px 0' }}>
        <p style={{ fontSize: '13px', color: '#8c8c8c', marginBottom: '8px' }}>
          Supported formats: .pdf, .txt
        </p>
        <p style={{ fontSize: '12px', color: '#b8b8b8', lineHeight: '1.6' }}>
          Documents will be processed and indexed for search.
        </p>
      </div>
    </Card>
  );
});
