/**
 * Loading Component
 *
 * Reusable loading indicator with custom messages
 */
import { Spin, Space, Typography } from 'antd';
import { LoadingOutlined } from '@ant-design/icons';

const { Text } = Typography;

interface LoadingProps {
  tip?: string;
  size?: 'small' | 'default' | 'large';
}

export default function Loading({ tip = '加载中...', size = 'default' }: LoadingProps) {
  return (
    <div
      style={{
        display: 'flex',
        justifyContent: 'center',
        alignItems: 'center',
        height: '100%',
        minHeight: 200,
      }}
    >
      <Space direction="vertical" align="center">
        <Spin
          indicator={<LoadingOutlined style={{ fontSize: size === 'large' ? 32 : 24 }} spin />}
          size={size}
        />
        {tip && <Text type="secondary">{tip}</Text>}
      </Space>
    </div>
  );
}

/**
 * Inline Loading Component
 */
export function InlineLoading({ text = '处理中...' }: { text?: string }) {
  return (
    <Space size="small">
      <Spin size="small" />
      <Text type="secondary" style={{ fontSize: 12 }}>
        {text}
      </Text>
    </Space>
  );
}
