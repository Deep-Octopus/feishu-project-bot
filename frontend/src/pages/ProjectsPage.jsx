import React, { useEffect, useState } from 'react'
import { Table, Button, Modal, Form, Input, DatePicker, Select, Space, Tag, message } from 'antd'
import { PlusOutlined, EditOutlined, DeleteOutlined } from '@ant-design/icons'
import { projectsApi } from '../api'
import dayjs from 'dayjs'

const STATUS_MAP = { active: ['进行中', 'blue'], completed: ['已完成', 'green'], paused: ['已暂停', 'orange'] }

export default function ProjectsPage() {
  const [projects, setProjects] = useState([])
  const [loading, setLoading] = useState(false)
  const [modalOpen, setModalOpen] = useState(false)
  const [editing, setEditing] = useState(null)
  const [form] = Form.useForm()

  const load = async () => {
    setLoading(true)
    try {
      const { data } = await projectsApi.list()
      setProjects(data)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => { load() }, [])

  const openCreate = () => { setEditing(null); form.resetFields(); setModalOpen(true) }
  const openEdit = (record) => {
    setEditing(record)
    form.setFieldsValue({
      ...record,
      start_date: record.start_date ? dayjs(record.start_date) : null,
      end_date: record.end_date ? dayjs(record.end_date) : null,
    })
    setModalOpen(true)
  }

  const handleSubmit = async () => {
    const values = await form.validateFields()
    const payload = {
      ...values,
      start_date: values.start_date?.toISOString(),
      end_date: values.end_date?.toISOString(),
    }
    if (editing) {
      await projectsApi.update(editing.id, payload)
      message.success('更新成功')
    } else {
      await projectsApi.create(payload)
      message.success('创建成功')
    }
    setModalOpen(false)
    load()
  }

  const handleDelete = async (id) => {
    await projectsApi.delete(id)
    message.success('删除成功')
    load()
  }

  const columns = [
    { title: '项目名称', dataIndex: 'name', key: 'name' },
    { title: '描述', dataIndex: 'description', key: 'description', ellipsis: true },
    { title: '飞书群ID', dataIndex: 'group_id', key: 'group_id' },
    {
      title: '状态', dataIndex: 'status', key: 'status',
      render: (s) => <Tag color={STATUS_MAP[s]?.[1]}>{STATUS_MAP[s]?.[0] || s}</Tag>
    },
    { title: '结束日期', dataIndex: 'end_date', key: 'end_date', render: (d) => d ? dayjs(d).format('YYYY-MM-DD') : '-' },
    {
      title: '操作', key: 'action',
      render: (_, record) => (
        <Space>
          <Button size="small" icon={<EditOutlined />} onClick={() => openEdit(record)}>编辑</Button>
          <Button size="small" danger icon={<DeleteOutlined />} onClick={() => handleDelete(record.id)}>删除</Button>
        </Space>
      )
    },
  ]

  return (
    <>
      <div style={{ marginBottom: 16, display: 'flex', justifyContent: 'space-between' }}>
        <h2 style={{ margin: 0 }}>项目管理</h2>
        <Button type="primary" icon={<PlusOutlined />} onClick={openCreate}>新建项目</Button>
      </div>
      <Table columns={columns} dataSource={projects} rowKey="id" loading={loading} />
      <Modal title={editing ? '编辑项目' : '新建项目'} open={modalOpen} onOk={handleSubmit} onCancel={() => setModalOpen(false)}>
        <Form form={form} layout="vertical">
          <Form.Item name="name" label="项目名称" rules={[{ required: true }]}>
            <Input />
          </Form.Item>
          <Form.Item name="description" label="项目描述">
            <Input.TextArea rows={3} />
          </Form.Item>
          <Form.Item name="group_id" label="飞书群ID">
            <Input placeholder="oc_xxxxxxxx" />
          </Form.Item>
          <Form.Item name="start_date" label="开始日期">
            <DatePicker style={{ width: '100%' }} />
          </Form.Item>
          <Form.Item name="end_date" label="计划结束日期">
            <DatePicker style={{ width: '100%' }} />
          </Form.Item>
          <Form.Item name="status" label="状态">
            <Select options={[
              { value: 'active', label: '进行中' },
              { value: 'completed', label: '已完成' },
              { value: 'paused', label: '已暂停' },
            ]} />
          </Form.Item>
        </Form>
      </Modal>
    </>
  )
}
