/**
 * Enhanced Chat Box Component
 *
 * Main chat interface with improved UX using all specialized components
 */
import { useEffect, useState } from 'react';
import { Layout, Spin, Modal, Space, Button } from 'antd';
import {
  ExclamationCircleOutlined,
  MenuFoldOutlined,
  MenuUnfoldOutlined,
} from '@ant-design/icons';
import { useNavigate } from 'react-router-dom';
import { useChatStore } from '@/store/chatStore';
import { useAuthStore } from '@/store/authStore';
import { useConfigStore } from '@/store/configStore';
import Sidebar from './Sidebar';
import MessageList from './MessageList';
import InputBox from './InputBox';
import { AttachmentList } from './DownloadButton';
import type { Attachment } from '@/types';

export default function ChatBox() {
  const navigate = useNavigate();
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
  const [previewModalOpen, setPreviewModalOpen] = useState(false);
  const [previewContent, setPreviewContent] = useState<string>('');

  const { user, logout } = useAuthStore();
  const { config, isConfigured } = useConfigStore();
  const {
    messages,
    isLoading,
    isSending,
    attachments,
    loadMessages,
    sendMessage,
    generateWorklog,
    clearMessages,
  } = useChatStore();

  const [inputValue, setInputValue] = useState('');

  // Check configuration on mount
  useEffect(() => {
    if (!isConfigured) {
      Modal.warning({
        title: '请先配置 Git 平台',
        content: '使用前需要先配置 GitLab 或 GitHub 的访问信息。',
        okText: '去配置',
        onOk: () => navigate('/config'),
      });
    }
  }, [isConfigured, navigate]);

  // Load messages on mount
  useEffect(() => {
    loadMessages();
  }, [loadMessages]);

  const handleSend = async () => {
    if (!inputValue.trim()) return;

    const content = inputValue;
    setInputValue('');

    try {
      await sendMessage(content);
    } catch (error) {
      console.error('Send message failed:', error);
    }
  };

  const handleQuickWorklog = async (timeRange: string) => {
    try {
      await generateWorklog(timeRange);
    } catch (error) {
      console.error('Generate worklog failed:', error);
    }
  };

  const handleClearHistory = async () => {
    Modal.confirm({
      title: '确认清空',
      icon: <ExclamationCircleOutlined />,
      content: '确定要清空所有聊天记录吗？此操作不可撤销。',
      okText: '确认',
      okType: 'danger',
      cancelText: '取消',
      onOk: async () => {
        try {
          await clearMessages();
        } catch (error) {
          console.error('Clear messages failed:', error);
        }
      },
    });
  };

  const handlePreview = (attachment: Attachment) => {
    try {
      const decodedContent = atob(attachment.content);
      setPreviewContent(decodedContent);
      setPreviewModalOpen(true);
    } catch (error) {
      console.error('Preview failed:', error);
    }
  };

  return (
    <Layout style={{ height: '100vh', marginLeft: sidebarCollapsed ? 80 : 250 }}>
      {/* Sidebar */}
      <Sidebar
        collapsed={sidebarCollapsed}
        onCollapse={setSidebarCollapsed}
        onQuickWorklog={handleQuickWorklog}
        onClearHistory={handleClearHistory}
      />

      {/* Main Content */}
      <Layout style={{ height: '100vh' }}>
        {/* Header */}
        <div style={{
          padding: '12px 16px',
          background: '#fff',
          borderBottom: '1px solid #f0f0f0',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
        }}>
          <Space>
            <Button
              type="text"
              icon={sidebarCollapsed ? <MenuUnfoldOutlined /> : <MenuFoldOutlined />}
              onClick={() => setSidebarCollapsed(!sidebarCollapsed)}
            />
            <span style={{ fontWeight: 500 }}>工作日志助手</span>
          </Space>

          <Space>
            {config?.default_platform === 'gitlab' ? (
              <span>🦊 GitLab</span>
            ) : config?.default_platform === 'github' ? (
              <span>🐙 GitHub</span>
            ) : null}
          </Space>
        </div>

        {/* Messages Area */}
        <div
          style={{
            flex: 1,
            overflowY: 'auto',
            background: '#f5f5f5',
          }}
        >
          {isLoading ? (
            <div style={{
              display: 'flex',
              justifyContent: 'center',
              alignItems: 'center',
              height: '100%'
            }}>
              <Spin size="large" tip="加载中..." />
            </div>
          ) : (
            <>
              <div style={{ maxWidth: 900, margin: '0 auto' }}>
                <MessageList messages={messages} isLoading={isSending} />
              </div>

              {/* Attachments */}
              {attachments && attachments.length > 0 && (
                <div style={{ maxWidth: 900, margin: '0 auto', paddingBottom: 16 }}>
                  <AttachmentList attachments={attachments} onPreview={handlePreview} />
                </div>
              )}
            </>
          )}
        </div>

        {/* Input Area */}
        <InputBox
          value={inputValue}
          onChange={setInputValue}
          onSend={handleSend}
          disabled={!isConfigured}
          loading={isSending}
        />
      </Layout>

      {/* Preview Modal */}
      <Modal
        title="文件预览"
        open={previewModalOpen}
        onCancel={() => setPreviewModalOpen(false)}
        footer={[
          <Button key="close" onClick={() => setPreviewModalOpen(false)}>
            关闭
          </Button>,
        ]}
        width={800}
        style={{ top: 20 }}
      >
        <div
          style={{
            maxHeight: '60vh',
            overflowY: 'auto',
            padding: '12px',
            background: '#f5f5f5',
            borderRadius: 4,
          }}
        >
          <pre style={{ whiteSpace: 'pre-wrap', wordBreak: 'break-word' }}>
            {previewContent}
          </pre>
        </div>
      </Modal>
    </Layout>
  );
}
