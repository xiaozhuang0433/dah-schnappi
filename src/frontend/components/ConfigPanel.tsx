/**
 * Configuration Panel Component
 *
 * User configuration interface for GitLab/GitHub settings (Phase 6: Full UI implementation)
 */
import { useEffect } from 'react';
import { Form, Input, Button, Card, Radio, Space, message, Spin } from 'antd';
import { SaveOutlined, GithubOutlined, GitlabOutlined } from '@ant-design/icons';
import { useNavigate } from 'react-router-dom';
import { useConfigStore } from '@/store/configStore';
import type { GitLabConfigUpdate, GitHubConfigUpdate } from '@/types';

export default function ConfigPanel() {
  const navigate = useNavigate();
  const { config, isLoading, fetchConfig, updateGitLabConfig, updateGitHubConfig } = useConfigStore();

  useEffect(() => {
    fetchConfig();
  }, [fetchConfig]);

  const onFinish = async (values: any) => {
    try {
      const platform = values.platform;

      if (platform === 'gitlab') {
        const data: GitLabConfigUpdate = {
          gitlab_url: values.gitlab_url,
          gitlab_token: values.gitlab_token,
        };
        await updateGitLabConfig(data);
      } else if (platform === 'github') {
        const data: GitHubConfigUpdate = {
          github_username: values.github_username,
          github_token: values.github_token,
        };
        await updateGitHubConfig(data);
      }

      message.success('配置保存成功');
    } catch (error) {
      message.error('配置保存失败');
    }
  };

  if (isLoading && !config) {
    return (
      <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100vh' }}>
        <Spin size="large" />
      </div>
    );
  }

  return (
    <div style={{ padding: '24px', maxWidth: '800px', margin: '0 auto' }}>
      <Card
        title={<><GitlabOutlined /> Git 平台配置</>}
        extra={
          <Button type="link" onClick={() => navigate('/')}>
            返回聊天
          </Button>
        }
      >
        <Form
          layout="vertical"
          onFinish={onFinish}
          initialValues={{
            platform: config?.default_platform || 'gitlab',
            gitlab_url: config?.gitlab_url || '',
            gitlab_token: '',
            github_username: config?.github_username || '',
            github_token: '',
          }}
        >
          <Form.Item
            label="默认平台"
            name="platform"
          >
            <Radio.Group>
              <Radio value="gitlab"><GitlabOutlined /> GitLab</Radio>
              <Radio value="github"><GithubOutlined /> GitHub</Radio>
            </Radio.Group>
          </Form.Item>

          <Card title="GitLab 配置" size="small" style={{ marginBottom: 16 }}>
            <Form.Item
              label="GitLab 服务器地址"
              name="gitlab_url"
              rules={[{ required: true, message: '请输入 GitLab 服务器地址' }]}
            >
              <Input placeholder="https://gitlab.example.com" />
            </Form.Item>

            <Form.Item
              label="GitLab 访问令牌"
              name="gitlab_token"
              extra="生成路径: User Settings → Access Tokens"
            >
              <Input.Password placeholder="glpat-..." />
            </Form.Item>
          </Card>

          <Card title="GitHub 配置" size="small" style={{ marginBottom: 16 }}>
            <Form.Item
              label="GitHub 用户名"
              name="github_username"
            >
              <Input placeholder="your-username" />
            </Form.Item>

            <Form.Item
              label="GitHub 访问令牌"
              name="github_token"
              extra="生成路径: Settings → Developer settings → Personal access tokens"
            >
              <Input.Password placeholder="ghp_..." />
            </Form.Item>
          </Card>

          <Form.Item>
            <Space>
              <Button type="primary" htmlType="submit" icon={<SaveOutlined />}>
                保存配置
              </Button>
              <Button onClick={() => navigate('/')}>
                取消
              </Button>
            </Space>
          </Form.Item>
        </Form>
      </Card>
    </div>
  );
}
