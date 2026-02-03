/**
 * Sidebar Component
 *
 * Navigation sidebar with user info and quick actions
 */
import { useState } from 'react';
import { Layout, Menu, Button, Space, Divider, Avatar, Typography, Dropdown } from 'antd';
import {
  SettingOutlined,
  ClearOutlined,
  LogoutOutlined,
  HistoryOutlined,
  QuestionCircleOutlined,
  MenuFoldOutlined,
  MenuUnfoldOutlined,
  CalendarOutlined,
  ClockCircleOutlined,
  FileTextOutlined,
  BarChartOutlined,
} from '@ant-design/icons';
import { useNavigate } from 'react-router-dom';
import { useAuthStore } from '@/store/authStore';
import type { MenuProps } from 'antd';

const { Sider } = Layout;
const { Text } = Typography;

interface SidebarProps {
  collapsed: boolean;
  onCollapse: (collapsed: boolean) => void;
  onQuickWorklog?: (timeRange: string) => void;
  onClearHistory?: () => void;
}

export default function Sidebar({ collapsed, onCollapse, onQuickWorklog, onClearHistory }: SidebarProps) {
  const navigate = useNavigate();
  const { user, logout } = useAuthStore();
  const [loading, setLoading] = useState(false);

  const handleLogout = async () => {
    setLoading(true);
    try {
      await logout();
      navigate('/login');
    } catch (error) {
      console.error('Logout failed:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleQuickWorklog = (timeRange: string) => {
    if (onQuickWorklog) {
      onQuickWorklog(timeRange);
    }
  };

  // Quick worklog menu items
  const worklogMenuItems: MenuProps['items'] = [
    {
      key: 'this-week',
      label: '本周工作日志',
      icon: <CalendarOutlined />,
      onClick: () => handleQuickWorklog('本周'),
    },
    {
      key: 'this-month',
      label: '本月工作日志',
      icon: <CalendarOutlined />,
      onClick: () => handleQuickWorklog('本月'),
    },
    {
      key: 'last-week',
      label: '上周工作日志',
      icon: <ClockCircleOutlined />,
      onClick: () => handleQuickWorklog('上周'),
    },
    {
      key: 'last-month',
      label: '上月工作日志',
      icon: <ClockCircleOutlined />,
      onClick: () => handleQuickWorklog('上月'),
    },
    {
      type: 'divider',
    },
    {
      key: 'commits',
      label: '最近提交',
      icon: <FileTextOutlined />,
      onClick: () => handleQuickWorklog('最近'),
    },
    {
      key: 'stats',
      label: '统计数据',
      icon: <BarChartOutlined />,
      onClick: () => handleQuickWorklog('统计'),
    },
  ];

  // Settings menu items
  const settingsMenuItems: MenuProps['items'] = [
    {
      key: 'config',
      label: '平台配置',
      icon: <SettingOutlined />,
      onClick: () => navigate('/config'),
    },
    {
      key: 'clear',
      label: '清空记录',
      icon: <ClearOutlined />,
      onClick: onClearHistory,
      danger: true,
    },
  ];

  return (
    <Sider
      collapsible
      collapsed={collapsed}
      onCollapse={onCollapse}
      width={250}
      theme="light"
      style={{
        overflow: 'auto',
        height: '100vh',
        position: 'fixed',
        left: 0,
        top: 0,
        bottom: 0,
        borderRight: '1px solid #f0f0f0',
      }}
    >
      {/* Logo / Title */}
      <div style={{
        padding: '16px',
        borderBottom: '1px solid #f0f0f0',
      }}>
        <Space style={{ width: '100%', justifyContent: 'space-between' }}>
          {!collapsed && (
            <Text strong style={{ fontSize: 16 }}>
              📝 工作日志助手
            </Text>
          )}
          <Button
            type="text"
            icon={collapsed ? <MenuUnfoldOutlined /> : <MenuFoldOutlined />}
            onClick={() => onCollapse(!collapsed)}
          />
        </Space>
      </div>

      {/* User Info */}
      <div style={{ padding: '16px' }}>
        <Space direction="vertical" size="small" style={{ width: '100%' }}>
          <Space>
            <Avatar icon={<FileTextOutlined />} style={{ backgroundColor: '#1890ff' }} />
            {!collapsed && (
              <Text strong>{user?.username || '用户'}</Text>
            )}
          </Space>
          {!collapsed && (
            <Text type="secondary" style={{ fontSize: 12 }}>
              {user?.email || ''}
            </Text>
          )}
        </Space>
      </div>

      <Divider style={{ margin: '8px 0' }} />

      {/* Quick Worklog Menu */}
      <div style={{ padding: collapsed ? '8px' : '8px 16px' }}>
        {!collapsed && (
          <Text
            type="secondary"
            style={{ fontSize: 12, marginBottom: 8, display: 'block' }}
          >
            🚀 快速生成
          </Text>
        )}
        <Menu
          mode="inline"
          selectedKeys={[]}
          items={worklogMenuItems}
          inlineCollapsed={collapsed}
        />
      </div>

      <Divider style={{ margin: '8px 0' }} />

      {/* Settings Menu */}
      <div style={{ padding: collapsed ? '8px' : '8px 16px' }}>
        {!collapsed && (
          <Text
            type="secondary"
            style={{ fontSize: 12, marginBottom: 8, display: 'block' }}
          >
            ⚙️ 设置
          </Text>
        )}
        <Menu
          mode="inline"
          selectedKeys={[]}
          items={settingsMenuItems}
          inlineCollapsed={collapsed}
        />
      </div>

      <Divider style={{ margin: '8px 0' }} />

      {/* Help */}
      <div style={{ padding: collapsed ? '8px' : '8px 16px' }}>
        {!collapsed && (
          <Text
            type="secondary"
            style={{ fontSize: 12, marginBottom: 8, display: 'block' }}
          >
            💡 帮助
          </Text>
        )}
        <Menu
          mode="inline"
          items={[
            {
              key: 'help',
              label: '使用指南',
              icon: <QuestionCircleOutlined />,
              onClick: () => {
                // Could open a modal or navigate to help page
                console.log('Open help');
              },
            },
          ]}
          inlineCollapsed={collapsed}
        />
      </div>

      {/* Logout Button (Always at bottom) */}
      <div style={{
        position: 'absolute',
        bottom: 16,
        left: 0,
        right: 0,
        padding: collapsed ? '0 8px' : '0 16px',
      }}>
        <Button
          block
          danger
          icon={<LogoutOutlined />}
          onClick={handleLogout}
          loading={loading}
        >
          {!collapsed && '登出'}
        </Button>
      </div>
    </Sider>
  );
}
