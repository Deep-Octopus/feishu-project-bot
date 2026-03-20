import React, { useState } from 'react'
import { Routes, Route, Link, useLocation } from 'react-router-dom'
import { Layout, Menu } from 'antd'
import {
  ProjectOutlined, CheckSquareOutlined, FileTextOutlined,
  BarChartOutlined, SettingOutlined,
} from '@ant-design/icons'
import ProjectsPage from './pages/ProjectsPage'
import TasksPage from './pages/TasksPage'
import ReportsPage from './pages/ReportsPage'
import StatisticsPage from './pages/StatisticsPage'
import SettingsPage from './pages/SettingsPage'

const { Sider, Content, Header } = Layout

const menuItems = [
  { key: '/projects', icon: <ProjectOutlined />, label: <Link to="/projects">项目管理</Link> },
  { key: '/tasks', icon: <CheckSquareOutlined />, label: <Link to="/tasks">任务管理</Link> },
  { key: '/reports', icon: <FileTextOutlined />, label: <Link to="/reports">日报查看</Link> },
  { key: '/statistics', icon: <BarChartOutlined />, label: <Link to="/statistics">统计分析</Link> },
  { key: '/settings', icon: <SettingOutlined />, label: <Link to="/settings">系统配置</Link> },
]

export default function App() {
  const location = useLocation()

  return (
    <Layout style={{ minHeight: '100vh' }}>
      <Sider theme="dark" width={200}>
        <div style={{ color: '#fff', padding: '16px', fontWeight: 'bold', fontSize: 14 }}>
          🤖 飞书项目机器人
        </div>
        <Menu
          theme="dark"
          mode="inline"
          selectedKeys={[location.pathname]}
          items={menuItems}
        />
      </Sider>
      <Layout>
        <Header style={{ background: '#fff', padding: '0 24px', borderBottom: '1px solid #f0f0f0' }}>
          <span style={{ fontSize: 16, fontWeight: 500 }}>飞书项目进度管理机器人 - 管理后台</span>
        </Header>
        <Content style={{ margin: 24, background: '#fff', padding: 24, borderRadius: 8 }}>
          <Routes>
            <Route path="/" element={<ProjectsPage />} />
            <Route path="/projects" element={<ProjectsPage />} />
            <Route path="/tasks" element={<TasksPage />} />
            <Route path="/reports" element={<ReportsPage />} />
            <Route path="/statistics" element={<StatisticsPage />} />
            <Route path="/settings" element={<SettingsPage />} />
          </Routes>
        </Content>
      </Layout>
    </Layout>
  )
}
