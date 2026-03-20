import React, { useEffect, useState } from 'react'
import { Table, Button, Modal, Form, Input, DatePicker, Select, Space, Tag, Progress, message, InputNumber } from 'antd'
import { PlusOutlined, EditOutlined, DeleteOutlined } from '@ant-design/icons'
import { tasksApi, projectsApi } from '../api'
import dayjs from 'dayjs'

const STATUS_MAP = {
  not_started: ['未开始', 'default'],
  in_progress: ['进行中', 'blue'],
  completed: ['已完成', 'green'],
  delayed: ['已延期', 'red'],
}

export default function TasksPage() {
  const [tasks, setTasks] = useState([])
  const [projects, setProjects] = useState([])
  const [projectId, setProjectId] = useState(null)
  const [loading, setLoading] = useState(false)
  const [modalOpen, setModalOpen] = useState(false)
  const [editing, setEditing] = useState(null)
  const [form] = Form.useForm()

  useEffect(() => {
    projectsApi.list().then(({ data }) => {
      setProjects(data)
      if (data.length > 0) setProjectId(data[0].id)
    })
  }, [])

  useEffect(() => {
    if (projectId) load()
  }, [projectId])

  const load = async () => {
    setLoading(true)
    try {
      const { data } = await tasksApi.list(projectId)
      setTasks(data)
    } finally {
      setLoading(false)
    }
  }

  const openCreate = () => { setEditing(null); form.resetFields(); form.setFieldValue('project_id', projectId); setModalOpen(true) }
  const openEdit = (record) => {
    setEditing(record)
    form.setFieldsValue({
      ...record,
      plan_start: record.plan_start ? dayjs(record.plan_start) : null,
      plan_end: record.plan_end ? dayjs(record.plan_end) : null,
    })
    setModalOpen(true)
  }

  const handleSubmit = async () => {
    const values = await form.validateFields()
    const payload = {
      ...values,
      plan_start: values.plan_start?.toISOString(),
      plan_end: values.plan_end?.toISOString(),
    }
    if (editing) {
      await tasksApi.update(editing.id, payload)
      message.success('更新成功')
    } else {
      await tasksApi.create(payload)
      message.success('创建成功')
    }
    setModalOpen(false)
    load()
  }

  const columns = [
    { title: '模块', dataIndex: 'module', key: 'module', width: 100 },
    { title: '任务名称', dataIndex: 'name', key: 'name' },
    { title: '负责人', dataIndex: 'assignee', key: 'assignee', width: 100 },
    {
      title: '状态', dataIndex: 'status', key: 'status', width: 100,
      render: (s) => <Tag color={STATUS_MAP[s]?.[1]}>{STATUS_MAP[s]?.[0] || s}</Tag>
    },
    {
      title: '完成度', dataIndex: 'progress', key: 'progress', width: 150,
      render: (p) => <Progress percent={p} size="small" />
    },
    {
      title: '风险', dataIndex: 'risk_flag', key: 'risk_flag', width: 60,
      render: (r) => r ? <Tag color="red">风险</Tag> : null
    },
    { title: '截止日期', dataIndex: 'plan_end', key: 'plan_end', width: 110, render: (d) => d ? dayjs(d).format('MM-DD') : '-' },
    {
      title: '操作', key: 'action', width: 120,
      render: (_, record) => (
        <Space>
          <Button size="small" icon={<EditOutlined />} onClick={() => openEdit(record)} />
          <Button size="small" danger icon={<DeleteOutlined />} onClick={async () => { await tasksApi.delete(record.id); load() }} />
        </Space>
      )
    },
  ]

  return (
    <>
      <div style={{ marginBottom: 16, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <Space>
          <h2 style={{ margin: 0 }}>任务管理</h2>
          <Select
            style={{ width: 200 }}
            value={projectId}
            onChange={setProjectId}
            options={projects.map(p => ({ value: p.id, label: p.name }))}
            placeholder="选择项目"
          />
        </Space>
        <Button type="primary" icon={<PlusOutlined />} onClick={openCreate} disabled={!projectId}>新建任务</Button>
      </div>
      <Table columns={columns} dataSource={tasks} rowKey="id" loading={loading} size="small" />
      <Modal title={editing ? '编辑任务' : '新建任务'} open={modalOpen} onOk={handleSubmit} onCancel={() => setModalOpen(false)}>
        <Form form={form} layout="vertical">
          <Form.Item name="project_id" hidden><Input /></Form.Item>
          <Form.Item name="module" label="所属模块"><Input /></Form.Item>
          <Form.Item name="name" label="任务名称" rules={[{ required: true }]}><Input /></Form.Item>
          <Form.Item name="assignee" label="负责人"><Input /></Form.Item>
          <Form.Item name="plan_start" label="计划开始"><DatePicker style={{ width: '100%' }} /></Form.Item>
          <Form.Item name="plan_end" label="计划结束"><DatePicker style={{ width: '100%' }} /></Form.Item>
          <Form.Item name="status" label="状态">
            <Select options={Object.entries(STATUS_MAP).map(([v, [l]]) => ({ value: v, label: l }))} />
          </Form.Item>
          <Form.Item name="progress" label="完成度(%)">
            <InputNumber min={0} max={100} style={{ width: '100%' }} />
          </Form.Item>
          <Form.Item name="latest_update" label="最新进展"><Input.TextArea rows={2} /></Form.Item>
        </Form>
      </Modal>
    </>
  )
}
