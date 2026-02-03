/**
 * Input Box Component
 *
 * Message input with auto-resize, quick actions, and file attachment support
 */
import { useState, KeyboardEvent } from 'react';
import { Input, Button, Space, Dropdown, Typography } from 'antd';
import {
  SendOutlined,
  PlusOutlined,
  ClockCircleOutlined,
  CalendarOutlined,
  FileTextOutlined,
} from '@ant-design/icons';

const { TextArea } = Input;
const { Text } = Typography;

interface InputBoxProps {
  value: string;
  onChange: (value: string) => void;
  onSend: () => void;
  disabled?: boolean;
  loading?: boolean;
}

// Quick action suggestions
const quickActions = [
  { key: 'this-week', label: '本周工作日志', icon: <CalendarOutlined />, value: '帮我生成本周的工作日志' },
  { key: 'this-month', label: '本月工作日志', icon: <CalendarOutlined />, value: '帮我生成本月的工作日志' },
  { key: 'last-week', label: '上周工作日志', icon: <ClockCircleOutlined />, value: '帮我生成上周的工作日志' },
  { key: 'commits', label: '最近提交', icon: <FileTextOutlined />, value: '查看最近的提交记录' },
];

export default function InputBox({ value, onChange, onSend, disabled, loading }: InputBoxProps) {
  const [isFocused, setIsFocused] = useState(false);

  const handleKeyDown = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      if (!disabled && value.trim()) {
        onSend();
      }
    }
  };

  const handleQuickAction = (actionValue: string) => {
    onChange(actionValue);
    // Auto-send after a short delay for better UX
    setTimeout(() => {
      onSend();
    }, 100);
  };

  return (
    <div style={{
      padding: '16px',
      background: '#fff',
      borderTop: '1px solid #f0f0f0',
    }}>
      {/* Quick Actions */}
      <div style={{ marginBottom: '12px' }}>
        <Space size="small" wrap>
          <Text type="secondary" style={{ fontSize: 12, marginRight: 8 }}>
            快捷操作:
          </Text>
          {quickActions.slice(0, 3).map((action) => (
            <Button
              key={action.key}
              size="small"
              icon={action.icon}
              onClick={() => handleQuickAction(action.value)}
              disabled={loading}
            >
              {action.label}
            </Button>
          ))}
        </Space>
      </div>

      {/* Input Area */}
      <div
        style={{
          display: 'flex',
          gap: '8px',
          alignItems: 'flex-end',
        }}
      >
        <div style={{ flex: 1 }}>
          <TextArea
            value={value}
            onChange={(e) => onChange(e.target.value)}
            onKeyDown={handleKeyDown}
            onFocus={() => setIsFocused(true)}
            onBlur={() => setIsFocused(false)}
            placeholder="输入消息... (Enter 发送, Shift+Enter 换行)"
            autoSize={{ minRows: 1, maxRows: 6 }}
            disabled={disabled}
            style={{
              resize: 'none',
              borderRadius: 8,
            }}
          />
        </div>

        <div style={{ display: 'flex', flexDirection: 'column', gap: 4 }}>
          {/* More quick actions dropdown */}
          <Dropdown
            menu={{
              items: quickActions.map((action) => ({
                key: action.key,
                label: action.label,
                icon: action.icon,
                onClick: () => handleQuickAction(action.value),
              })),
            }}
            trigger={['click']}
          >
            <Button
              icon={<PlusOutlined />}
              disabled={loading}
              style={{ marginBottom: 4 }}
            />
          </Dropdown>

          {/* Send button */}
          <Button
            type="primary"
            icon={<SendOutlined />}
            onClick={onSend}
            disabled={disabled || !value.trim()}
            loading={loading}
            style={{ height: 40 }}
          >
            发送
          </Button>
        </div>
      </div>

      {/* Hint text */}
      {!isFocused && value.length === 0 && (
        <div style={{ marginTop: 8 }}>
          <Text type="secondary" style={{ fontSize: 12 }}>
            💡 提示：可以问"本周有哪些提交？"或"生成本月工作日志"
          </Text>
        </div>
      )}
    </div>
  );
}
