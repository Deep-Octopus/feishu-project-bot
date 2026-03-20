import React, { useEffect, useState } from 'react'
import { Card, Form, Input, Switch, Button, message, Descriptions, Tag } from 'antd'
import { configApi } from '../api'

export default function SettingsPage() {
  const [config, setConfig] = useState(null)

  useEffect(() => {
    configApi.get().then(({ data }) => setConfig(data))
  }, [])

  if (!config) return null

  return (
    <>
      <h2>系统配置</h2>
      <Card title="飞书配置" style={{ marginBottom: 16 }}>
        <Descriptions column={1} bordered size="small">
          <Descriptions.Item label="App ID">{config.feishu.app_id || <Tag color="red">未配置</Tag>}</Descriptions.Item>
          <Descriptions.Item label="App Secret">{config.feishu.app_secret || <Tag color="red">未配置</Tag>}</Descriptions.Item>
          <Descriptions.Item label="回调地址">
            <code>{window.location.origin}/api/v1/feishu/callback</code>
          </Descriptions.Item>
        </Descriptions>
      </Card>

      <Card title="AI配置（硅基流动）" style={{ marginBottom: 16 }}>
        <Descriptions column={1} bordered size="small">
          <Descriptions.Item label="API地址">{config.siliconflow.base_url}</Descriptions.Item>
          <Descriptions.Item label="模型">{config.siliconflow.model}</Descriptions.Item>
          <Descriptions.Item label="Temperature">{config.siliconflow.temperature}</Descriptions.Item>
          <Descriptions.Item label="Max Tokens">{config.siliconflow.max_tokens}</Descriptions.Item>
        </Descriptions>
      </Card>

      <Card title="功能开关">
        <Descriptions column={1} bordered size="small">
          <Descriptions.Item label="AI日报解析">
            <Tag color={config.features.enable_ai_parsing ? 'green' : 'default'}>
              {config.features.enable_ai_parsing ? '已开启' : '已关闭'}
            </Tag>
          </Descriptions.Item>
          <Descriptions.Item label="自动提醒">
            <Tag color={config.features.enable_auto_reminder ? 'green' : 'default'}>
              {config.features.enable_auto_reminder ? '已开启' : '已关闭'}
            </Tag>
          </Descriptions.Item>
          <Descriptions.Item label="风险预警">
            <Tag color={config.features.enable_risk_warning ? 'green' : 'default'}>
              {config.features.enable_risk_warning ? '已开启' : '已关闭'}
            </Tag>
          </Descriptions.Item>
        </Descriptions>
        <p style={{ marginTop: 12, color: '#888', fontSize: 12 }}>
          如需修改配置，请编辑服务器上的 config/config.yaml 文件并重启服务。
        </p>
      </Card>
    </>
  )
}
