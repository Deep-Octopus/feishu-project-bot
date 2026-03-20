import React, { useEffect, useState } from 'react'
import { Row, Col, Card, Statistic, Select, Progress, Table, Space } from 'antd'
import { statisticsApi, projectsApi } from '../api'

export default function StatisticsPage() {
  const [projects, setProjects] = useState([])
  const [projectId, setProjectId] = useState(null)
  const [overview, setOverview] = useState(null)
  const [stats, setStats] = useState(null)
  const [period, setPeriod] = useState('week')

  useEffect(() => {
    projectsApi.list().then(({ data }) => {
      setProjects(data)
      if (data.length > 0) setProjectId(data[0].id)
    })
  }, [])

  useEffect(() => {
    if (!projectId) return
    statisticsApi.overview(projectId).then(({ data }) => setOverview(data))
    statisticsApi.stats(projectId, period).then(({ data }) => setStats(data))
  }, [projectId, period])

  return (
    <>
      <div style={{ marginBottom: 16, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <h2 style={{ margin: 0 }}>统计分析</h2>
        <Space>
          <Select
            style={{ width: 180 }}
            value={projectId}
            onChange={setProjectId}
            options={projects.map(p => ({ value: p.id, label: p.name }))}
            placeholder="选择项目"
          />
          <Select
            value={period}
            onChange={setPeriod}
            options={[{ value: 'week', label: '本周' }, { value: 'month', label: '本月' }]}
          />
        </Space>
      </div>

      {overview && (
        <Row gutter={16} style={{ marginBottom: 24 }}>
          <Col span={6}>
            <Card><Statistic title="整体完成度" value={overview.overall_progress} suffix="%" /></Card>
          </Col>
          <Col span={6}>
            <Card><Statistic title="总任务数" value={overview.tasks?.length || 0} /></Card>
          </Col>
          <Col span={6}>
            <Card><Statistic title="风险任务" value={overview.risk_count} valueStyle={{ color: '#cf1322' }} /></Card>
          </Col>
          <Col span={6}>
            <Card>
              <div style={{ fontSize: 14, color: '#666', marginBottom: 8 }}>进度</div>
              <Progress percent={overview.overall_progress} />
            </Card>
          </Col>
        </Row>
      )}

      {stats && (
        <Row gutter={16}>
          <Col span={12}>
            <Card title="成员活跃度">
              <Table
                size="small"
                dataSource={stats.member_activity}
                rowKey="user_name"
                pagination={false}
                columns={[
                  { title: '成员', dataIndex: 'user_name' },
                  { title: '日报数', dataIndex: 'report_count' },
                ]}
              />
            </Card>
          </Col>
          <Col span={12}>
            <Card title="模块进度">
              <Table
                size="small"
                dataSource={stats.module_progress}
                rowKey="module"
                pagination={false}
                columns={[
                  { title: '模块', dataIndex: 'module' },
                  { title: '平均进度', dataIndex: 'avg_progress', render: (v) => <Progress percent={v} size="small" /> },
                ]}
              />
            </Card>
          </Col>
        </Row>
      )}
    </>
  )
}
