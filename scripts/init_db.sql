-- 飞书项目进度管理机器人 数据库初始化脚本

CREATE TYPE project_status AS ENUM ('active', 'completed', 'paused');
CREATE TYPE task_status AS ENUM ('not_started', 'in_progress', 'completed', 'delayed');

CREATE TABLE IF NOT EXISTS projects (
    id SERIAL PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    description TEXT,
    group_id VARCHAR(100) UNIQUE,
    start_date TIMESTAMP,
    end_date TIMESTAMP,
    status project_status DEFAULT 'active',
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS tasks (
    id SERIAL PRIMARY KEY,
    project_id INTEGER NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    module VARCHAR(100),
    name VARCHAR(200) NOT NULL,
    assignee VARCHAR(100),
    plan_start TIMESTAMP,
    plan_end TIMESTAMP,
    status task_status DEFAULT 'not_started',
    progress FLOAT DEFAULT 0.0,
    latest_update TEXT,
    risk_flag BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS daily_reports (
    id SERIAL PRIMARY KEY,
    project_id INTEGER NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    user_id VARCHAR(100),
    user_name VARCHAR(100),
    content TEXT NOT NULL,
    submit_time TIMESTAMP DEFAULT NOW(),
    message_id VARCHAR(200),
    is_external BOOLEAN DEFAULT FALSE,
    ai_parsed BOOLEAN DEFAULT FALSE,
    parsed_data TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS progress_logs (
    id SERIAL PRIMARY KEY,
    task_id INTEGER NOT NULL REFERENCES tasks(id) ON DELETE CASCADE,
    change_type VARCHAR(50),
    old_value VARCHAR(500),
    new_value VARCHAR(500),
    trigger_by VARCHAR(100),
    trigger_source VARCHAR(50),
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS reminder_configs (
    id SERIAL PRIMARY KEY,
    project_id INTEGER NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    enabled BOOLEAN DEFAULT TRUE,
    days_before VARCHAR(50) DEFAULT '3,1',
    reminder_time VARCHAR(10) DEFAULT '09:00',
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_tasks_project_id ON tasks(project_id);
CREATE INDEX IF NOT EXISTS idx_tasks_status ON tasks(status);
CREATE INDEX IF NOT EXISTS idx_tasks_plan_end ON tasks(plan_end);
CREATE INDEX IF NOT EXISTS idx_daily_reports_project_id ON daily_reports(project_id);
CREATE INDEX IF NOT EXISTS idx_daily_reports_submit_time ON daily_reports(submit_time);
CREATE INDEX IF NOT EXISTS idx_daily_reports_user_name ON daily_reports(user_name);
CREATE INDEX IF NOT EXISTS idx_progress_logs_task_id ON progress_logs(task_id);
CREATE INDEX IF NOT EXISTS idx_projects_group_id ON projects(group_id);

-- Auto-update updated_at trigger
CREATE OR REPLACE FUNCTION update_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER projects_updated_at BEFORE UPDATE ON projects
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();

CREATE TRIGGER tasks_updated_at BEFORE UPDATE ON tasks
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();
