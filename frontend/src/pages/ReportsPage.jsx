import React, { useEffect, useState } from 'react'
import { Table, Select, Space, Input, DatePicker } from 'antd'
import { reportsApi, projectsApi } from '../api'
import dayjs from 'dayjs'

export default function ReportsPage() {
  const [reports, setReports] = useState([])
  const [projects, setProjects] = useState([])
  const [projectId, setProjectId] = useState(null)
  const [loading, setLoading] = useState(false)
  const [userName, setUserName] = useState('')
  const [date, setDate] = useState(null)
  const [page, setPage] = useState(1)
  const [total, setTotal] = useState(0)

  useEffect(() => {
    projectsApi.list().then(({ data }) => {
      setProjects(data)
      if (data.length > 0) setProjectId(data[0].id)
    })
  }, [])

  useEffect(() => {
    if (projectId) load()
  }, [projectId, page])

  const load = async () => {
    setLoading(true)
    try {
      const { data } = await reportsApi.list({
        project_id: projectId,
        user_name: userName || undefined,
        date: date ? date.format('YYYY-MM-DD') : undefined,
        page,
        page_size: 20,
      })
      setReports(data.items)
      setTotal(data.total)
    } finally {
      setLoading(false)
    }
  }

  const columns = [
    { title: '提交人', dataIndex: 'user_name', key: 'user_name', width: 100 },
    { title: '提交时间', dataIndex: 'submit_time', key: 'submit_time', width: 160, render: (t) => dayjs(t).format('YYYY-MM-DD HH:mm') },
    { title: '日报内容', dataIndex: 'content', key: 'content', ellipsis: true },
    { title: 'AI解析', dataIndex: 'ai_parsed', key: 'ai_parsed', width: 80, render: (v) => v ? '✅' : '❌' },
  ]

  return (
    <>
      <div style={{ marginBottom: 16 }}>
        <h2 style={{ margin: '0 0 12px' }}>日报查看</h2>
        <Space wrap>
          <Select
            style={{ width: 180 }}
            value={projectId}
            onChange={(v) => { setProjectId(v); setPage(1) }}
            options={projects.map(p => ({ value: p.id, label: p.name }))}
            placeholder="选择项目"
          />
          <Input.Search
            placeholder="按成员搜索"
            style={{ width: 160 }}
            onSearch={(v) => { setUserName(v); setPage(1); load() }}
            allowClear
          />
          <DatePicker
            placeholder="按日期筛选"
            onChange={(d) => { setDate(d); setPage(1) }}
          />
        </Space>
      </div>
      <Table
        columns={columns}
        dataSource={reports}
        rowKey="id"
        loading={loading}
        pagination={{ current: page, total, pageSize: 20, onChange: setPage }}
        expandable={{
          expandedRowRender: (record) => <p style={{ margin: 0, whiteSpace: 'pre-wrap' }}>{record.content}</p>,
        }}
      />
    </>
  )
}
