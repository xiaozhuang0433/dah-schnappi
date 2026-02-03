/**
 * Message List Component
 *
 * Displays chat messages with Markdown rendering and user/assistant differentiation
 */
import { useEffect, useRef } from 'react';
import { Card, Typography, Space, Tag, Tooltip } from 'antd';
import {
  UserOutlined,
  RobotOutlined,
  ClockCircleOutlined,
  CheckCircleOutlined,
  CloseCircleOutlined,
} from '@ant-design/icons';
import ReactMarkdown from 'react-markdown';
import type { ChatMessage } from '@/types';
import dayjs from 'dayjs';
import relativeTime from 'dayjs/plugin/relativeTime';
import 'dayjs/locale/zh-cn';

dayjs.extend(relativeTime);
dayjs.locale('zh-cn');

const { Text } = Typography;

interface MessageListProps {
  messages: ChatMessage[];
  isLoading?: boolean;
}

export default function MessageList({ messages, isLoading }: MessageListProps) {
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  if (messages.length === 0 && !isLoading) {
    return (
      <div style={{
        display: 'flex',
        justifyContent: 'center',
        alignItems: 'center',
        height: '100%',
        padding: '24px'
      }}>
        <Card style={{ textAlign: 'center', maxWidth: 400 }}>
          <RobotOutlined style={{ fontSize: 48, color: '#1890ff', marginBottom: 16 }} />
          <Text type="secondary" style={{ fontSize: 16 }}>
            👋 欢迎使用工作日志助手！
          </Text>
          <br />
          <Text type="secondary" style={{ fontSize: 14 }}>
            试试问这些问题：
          </Text>
          <ul style={{ textAlign: 'left', marginTop: 16, paddingLeft: 24 }}>
            <li>"帮我生成本周的工作日志"</li>
            <li>"最近有哪些提交？"</li>
            <li>"本月完成了什么项目？"</li>
          </ul>
        </Card>
      </div>
    );
  }

  const renderMetadata = (message: ChatMessage) => {
    if (!message.metadata) return null;

    const { model, usage, processing_time, tool_calls, error } = message.metadata;

    return (
      <Space direction="vertical" size="small" style={{ marginTop: 8, fontSize: 12 }}>
        {error && (
          <Tag icon={<CloseCircleOutlined />} color="error">
            {error}
          </Tag>
        )}
        {tool_calls && tool_calls.length > 0 && (
          <Tag icon={<CheckCircleOutlined />} color="success">
            使用了 {tool_calls.length} 个工具
          </Tag>
        )}
        {processing_time && (
          <Text type="secondary" style={{ fontSize: 11 }}>
            ⏱️ {processing_time.toFixed(2)}s
          </Text>
        )}
        {usage && (
          <Text type="secondary" style={{ fontSize: 11 }}>
            🔢 {usage.total_tokens} tokens
          </Text>
        )}
      </Space>
    );
  };

  return (
    <div style={{ padding: '16px' }}>
      {messages.map((message, index) => (
        <div
          key={message.id || index}
          style={{
            display: 'flex',
            justifyContent: message.role === 'user' ? 'flex-end' : 'flex-start',
            marginBottom: '16px',
            animation: 'fadeIn 0.3s ease-in'
          }}
        >
          <div style={{ maxWidth: '70%', display: 'flex', flexDirection: 'column' }}>
            {/* Message Header */}
            <div style={{
              display: 'flex',
              alignItems: 'center',
              marginBottom: '4px',
              justifyContent: message.role === 'user' ? 'flex-end' : 'flex-start',
              gap: '8px'
            }}>
              {message.role === 'user' ? (
                <>
                  <Text type="secondary" style={{ fontSize: 12 }}>
                    {dayjs(message.created_at).fromNow()}
                  </Text>
                  <UserOutlined style={{ color: '#1890ff' }} />
                </>
              ) : (
                <>
                  <RobotOutlined style={{ color: '#52c41a' }} />
                  <Text type="secondary" style={{ fontSize: 12 }}>
                    {dayjs(message.created_at).fromNow()}
                  </Text>
                </>
              )}
            </div>

            {/* Message Content */}
            <Card
              size="small"
              style={{
                backgroundColor: message.role === 'user' ? '#1890ff' : '#fff',
                color: message.role === 'user' ? '#fff' : '#000',
                border: message.role === 'user' ? 'none' : '1px solid #f0f0f0',
                borderRadius: 12,
                boxShadow: '0 1px 2px rgba(0,0,0,0.05)',
              }}
              bodyStyle={{ padding: '12px 16px' }}
            >
              {message.role === 'assistant' ? (
                <div className="markdown-content">
                  <ReactMarkdown
                    components={{
                      // Custom styling for markdown elements
                      h1: ({ node, ...props }) => <h1 style={{ fontSize: '1.5em', marginTop: 0 }} {...props} />,
                      h2: ({ node, ...props }) => <h2 style={{ fontSize: '1.3em', marginTop: '0.5em' }} {...props} />,
                      h3: ({ node, ...props }) => <h3 style={{ fontSize: '1.1em', marginTop: '0.5em' }} {...props} />,
                      p: ({ node, ...props }) => <p style={{ marginBottom: '0.5em' }} {...props} />,
                      ul: ({ node, ...props }) => <ul style={{ marginBottom: '0.5em', paddingLeft: '1.5em' }} {...props} />,
                      ol: ({ node, ...props }) => <ol style={{ marginBottom: '0.5em', paddingLeft: '1.5em' }} {...props} />,
                      li: ({ node, ...props }) => <li style={{ marginBottom: '0.25em' }} {...props} />,
                      code: ({ node, inline, ...props }) =>
                        inline ? (
                          <code style={{
                            background: 'rgba(0,0,0,0.06)',
                            padding: '2px 6px',
                            borderRadius: '3px',
                            fontSize: '0.9em'
                          }} {...props} />
                        ) : (
                          <code style={{
                            display: 'block',
                            background: 'rgba(0,0,0,0.06)',
                            padding: '12px',
                            borderRadius: '4px',
                            overflowX: 'auto',
                            fontSize: '0.9em'
                          }} {...props} />
                        )
                    }}
                  >
                    {message.content}
                  </ReactMarkdown>
                </div>
              ) : (
                <Text style={{
                  color: message.role === 'user' ? '#fff' : '#000',
                  whiteSpace: 'pre-wrap',
                  wordBreak: 'break-word'
                }}>
                  {message.content}
                </Text>
              )}

              {renderMetadata(message)}
            </Card>
          </div>
        </div>
      ))}

      {/* Invisible div for auto-scroll */}
      <div ref={messagesEndRef} />
    </div>
  );
}
