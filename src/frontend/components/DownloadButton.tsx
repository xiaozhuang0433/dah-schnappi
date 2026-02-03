/**
 * Download Button Component
 *
 * Handles file downloads with preview and multiple format support
 */
import { Button, Space, Typography, Dropdown, message } from 'antd';
import {
  DownloadOutlined,
  FileMarkdownOutlined,
  FileTextOutlined,
  CopyOutlined,
  EyeOutlined,
} from '@ant-design/icons';
import type { Attachment } from '@/types';

const { Text } = Typography;

interface DownloadButtonProps {
  attachment: Attachment;
  onPreview?: (attachment: Attachment) => void;
}

export default function DownloadButton({ attachment, onPreview }: DownloadButtonProps) {
  const { filename, type, size } = attachment;

  // Format file size
  const formatSize = (bytes?: number): string => {
    if (!bytes) return '';
    if (bytes < 1024) return `${bytes} B`;
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
    return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
  };

  // Decode base64 and download
  const handleDownload = () => {
    try {
      const byteCharacters = atob(attachment.content);
      const byteNumbers = new Array(byteCharacters.length);
      for (let i = 0; i < byteCharacters.length; i++) {
        byteNumbers[i] = byteCharacters.charCodeAt(i);
      }
      const byteArray = new Uint8Array(byteNumbers);
      const blob = new Blob([byteArray], { type: 'text/markdown' });
      const url = URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = filename;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      URL.revokeObjectURL(url);

      message.success(`已下载 ${filename}`);
    } catch (error) {
      message.error('下载失败');
      console.error('Download error:', error);
    }
  };

  // Copy content to clipboard
  const handleCopy = async () => {
    try {
      // Decode base64
      const decodedContent = atob(attachment.content);
      await navigator.clipboard.writeText(decodedContent);
      message.success('已复制到剪贴板');
    } catch (error) {
      message.error('复制失败');
      console.error('Copy error:', error);
    }
  };

  // Get file icon
  const getFileIcon = () => {
    switch (type) {
      case 'markdown':
        return <FileMarkdownOutlined style={{ color: '#1890ff' }} />;
      case 'text':
        return <FileTextOutlined style={{ color: '#52c41a' }} />;
      default:
        return <FileTextOutlined />;
    }
  };

  const menuItems = [
    {
      key: 'download',
      label: '下载文件',
      icon: <DownloadOutlined />,
      onClick: handleDownload,
    },
    {
      key: 'copy',
      label: '复制内容',
      icon: <CopyOutlined />,
      onClick: handleCopy,
    },
    ...(onPreview ? [{
      key: 'preview',
      label: '预览',
      icon: <EyeOutlined />,
      onClick: () => onPreview(attachment),
    }] : []),
  ];

  return (
    <div style={{
      padding: '12px',
      background: '#f5f5f5',
      borderRadius: 8,
      border: '1px solid #f0f0f0',
    }}>
      <Space direction="vertical" style={{ width: '100%' }} size="small">
        {/* File Info */}
        <Space>
          {getFileIcon()}
          <Text strong>{filename}</Text>
          {size && (
            <Text type="secondary" style={{ fontSize: 12 }}>
              ({formatSize(size)})
            </Text>
          )}
        </Space>

        {/* Action Buttons */}
        <Space>
          <Button
            type="primary"
            size="small"
            icon={<DownloadOutlined />}
            onClick={handleDownload}
          >
            下载
          </Button>
          <Button
            size="small"
            icon={<CopyOutlined />}
            onClick={handleCopy}
          >
            复制
          </Button>
          {onPreview && (
            <Button
              size="small"
              icon={<EyeOutlined />}
              onClick={() => onPreview(attachment)}
            >
              预览
            </Button>
          )}
        </Space>
      </Space>
    </div>
  );
}

/**
 * Attachment List Component
 */
interface AttachmentListProps {
  attachments: Attachment[];
  onPreview?: (attachment: Attachment) => void;
}

export function AttachmentList({ attachments, onPreview }: AttachmentListProps) {
  if (attachments.length === 0) return null;

  return (
    <div style={{ marginTop: 16 }}>
      <Text strong style={{ marginBottom: 8, display: 'block' }}>
        📎 附件 ({attachments.length})
      </Text>
      <Space direction="vertical" style={{ width: '100%' }} size="middle">
        {attachments.map((attachment, index) => (
          <DownloadButton
            key={index}
            attachment={attachment}
            onPreview={onPreview}
          />
        ))}
      </Space>
    </div>
  );
}
