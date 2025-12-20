-- ========== 项目 / 任务集合 ==========
CREATE TABLE projects (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workspace_id UUID REFERENCES workspaces(id) ON DELETE SET NULL,
    owner_id UUID REFERENCES users(id) ON DELETE SET NULL,
    title TEXT NOT NULL,
    description TEXT,
    start_date DATE,
    due_date DATE,
    archived BOOLEAN DEFAULT FALSE,
    metadata JSONB DEFAULT '{}'::JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
    deleted_at TIMESTAMP WITH TIME ZONE NULL
);
CREATE INDEX idx_projects_workspace ON projects(workspace_id);
CREATE INDEX idx_projects_owner ON projects(owner_id);

-- ========== 任务（主表） ==========
CREATE TABLE tasks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID REFERENCES projects(id) ON DELETE SET NULL,
    workspace_id UUID REFERENCES workspaces(id) ON DELETE SET NULL,
    creator_id UUID REFERENCES users(id) ON DELETE SET NULL,
    assignee_id UUID REFERENCES users(id) ON DELETE SET NULL,   -- 默认给自己加
    parent_task_id UUID REFERENCES tasks(id) ON DELETE CASCADE, -- 父任务ID
    title TEXT NOT NULL,
    description TEXT,
    status task_status DEFAULT 'backlog',
    priority priority_level DEFAULT 'medium',
    estimated_minutes INTEGER, -- 估时（分钟）
    actual_minutes INTEGER DEFAULT 0,
    due_at TIMESTAMP WITH TIME ZONE,
    started_at TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE,
    is_recurring BOOLEAN DEFAULT FALSE,
    recurrence_rule JSONB, -- RFC5545 或自定义频率
    recurrence_frequency recurrence_freq DEFAULT 'none',
    recurrence_meta JSONB DEFAULT '{}'::JSONB,
    metadata JSONB DEFAULT '{}'::JSONB, -- 额外扩展
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
    deleted_at TIMESTAMP WITH TIME ZONE NULL
);
CREATE INDEX idx_tasks_project ON tasks(project_id);
CREATE INDEX idx_tasks_assignee ON tasks(assignee_id);
CREATE INDEX idx_tasks_status ON tasks(status);
CREATE INDEX idx_tasks_workspace ON tasks(workspace_id);
CREATE INDEX idx_tasks_due ON tasks(due_at);

-- 任务依赖（任务 A 依赖于任务 B）
CREATE TABLE task_dependencies (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    task_id UUID REFERENCES tasks(id) ON DELETE CASCADE, -- 子任务/后续任务
    depends_on_task_id UUID REFERENCES tasks(id) ON DELETE CASCADE, -- 前置任务
    relation_type TEXT DEFAULT 'finish_to_start', -- 可扩展
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
    UNIQUE (task_id, depends_on_task_id)
);

-- 任务历史/活动（用于审计）
CREATE TABLE task_activity_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    task_id UUID REFERENCES tasks(id) ON DELETE CASCADE,
    user_id UUID REFERENCES users(id),
    action TEXT NOT NULL, -- 'status_change','comment','assign','update' 等
    metadata JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now()
);
CREATE INDEX idx_task_activity_task ON task_activity_logs(task_id);