-- 开启扩展（需要超级权限）
CREATE EXTENSION IF NOT EXISTS pgcrypto; -- 用于 gen_random_uuid()

-- ========== 自定义 ENUM 类型 ==========
CREATE TYPE user_role AS ENUM ('user','admin','owner','guest','support');
CREATE TYPE task_status AS ENUM ('backlog','todo','in_progress','blocked','done','cancelled');
CREATE TYPE priority_level AS ENUM ('low','medium','high','critical');
CREATE TYPE reminder_channel AS ENUM ('email','push','sms','in_app');
CREATE TYPE recurrence_freq AS ENUM ('none','daily','weekly','monthly','yearly','custom');
CREATE TYPE attachment_type AS ENUM ('file','image','audio','video','document','other');
CREATE TYPE integration_kind AS ENUM ('google_calendar','outlook','notion','slack','github','custom');
CREATE TYPE payment_status AS ENUM ('trial','active','past_due','cancelled','expired');
CREATE TYPE oauth_provider AS ENUM ('google','apple','github','microsoft','custom');
CREATE TYPE notification_level AS ENUM ('info','warning','error','success');
CREATE TYPE ai_model_kind AS ENUM ('decomposer','planner','summarizer','reminder','chat','other');

-- ========== 基础用户与认证 ==========
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email TEXT UNIQUE NOT NULL,
    email_verified BOOLEAN DEFAULT FALSE,
    password_hash TEXT, -- nullable if oauth-only
    full_name TEXT,
    display_name TEXT,
    avatar_url TEXT,
    locale TEXT DEFAULT 'zh-CN',
    timezone TEXT DEFAULT 'Asia/Tokyo',
    role user_role NOT NULL DEFAULT 'user',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
    deleted_at TIMESTAMP WITH TIME ZONE NULL
);
CREATE INDEX idx_users_email ON users(email);

CREATE TABLE user_profiles (
    user_id UUID PRIMARY KEY REFERENCES users(id) ON DELETE CASCADE,
    bio TEXT,
    pronouns TEXT,
    job_title TEXT,
    organization TEXT,
    settings JSONB DEFAULT '{}'::JSONB, -- 自定义个人设置
    metadata JSONB DEFAULT '{}'::JSONB, -- 备用扩展
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT now()
);

CREATE TABLE sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    device_info TEXT,
    ip_address INET,
    user_agent TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
    last_active_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
    expires_at TIMESTAMP WITH TIME ZONE,
    revoked BOOLEAN DEFAULT FALSE
);

CREATE TABLE password_resets (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    token TEXT NOT NULL UNIQUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
    used BOOLEAN DEFAULT FALSE
);

CREATE TABLE email_verifications (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    token TEXT NOT NULL UNIQUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
    used BOOLEAN DEFAULT FALSE
);

-- ========== 组织/团队支持（可选） ==========
CREATE TABLE organizations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL,
    slug TEXT UNIQUE,
    owner_id UUID REFERENCES users(id),
    billing_info JSONB,
    settings JSONB DEFAULT '{}'::JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
    deleted_at TIMESTAMP WITH TIME ZONE NULL
);

CREATE TABLE organization_members (
    organization_id UUID REFERENCES organizations(id) ON DELETE CASCADE,
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    role user_role DEFAULT 'user',
    joined_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
    PRIMARY KEY (organization_id, user_id)
);

-- ========== 项目/工作区 ==========
CREATE TABLE workspaces (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id UUID REFERENCES organizations(id) ON DELETE SET NULL,
    owner_user_id UUID REFERENCES users(id) ON DELETE SET NULL,
    name TEXT NOT NULL,
    description TEXT,
    settings JSONB DEFAULT '{}'::JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
    deleted_at TIMESTAMP WITH TIME ZONE NULL
);

CREATE TABLE workspace_members (
    workspace_id UUID REFERENCES workspaces(id) ON DELETE CASCADE,
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    role user_role DEFAULT 'user',
    PRIMARY KEY (workspace_id, user_id)
);

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

-- ========== 标签/自定义字段 ==========
CREATE TABLE tags (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workspace_id UUID REFERENCES workspaces(id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    color TEXT,
    created_by UUID REFERENCES users(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
    UNIQUE (workspace_id, name)
);

CREATE TABLE custom_fields (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workspace_id UUID REFERENCES workspaces(id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    field_type TEXT NOT NULL, -- e.g., 'text','number','date','enum','boolean'
    config JSONB DEFAULT '{}'::JSONB, -- options etc.
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
    UNIQUE (workspace_id, name)
);

-- ========== 任务（主表） ==========
CREATE TABLE tasks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID REFERENCES projects(id) ON DELETE SET NULL,
    workspace_id UUID REFERENCES workspaces(id) ON DELETE SET NULL,
    creator_id UUID REFERENCES users(id) ON DELETE SET NULL,
    assignee_id UUID REFERENCES users(id) ON DELETE SET NULL,
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

-- 任务与标签（多对多）
CREATE TABLE task_tags (
    task_id UUID REFERENCES tasks(id) ON DELETE CASCADE,
    tag_id UUID REFERENCES tags(id) ON DELETE CASCADE,
    PRIMARY KEY (task_id, tag_id)
);

-- 任务与自定义字段值
CREATE TABLE task_custom_field_values (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    task_id UUID REFERENCES tasks(id) ON DELETE CASCADE,
    custom_field_id UUID REFERENCES custom_fields(id) ON DELETE CASCADE,
    value JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
    UNIQUE (task_id, custom_field_id)
);

-- 子任务（独立行或树形）
CREATE TABLE subtasks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    task_id UUID REFERENCES tasks(id) ON DELETE CASCADE,
    parent_subtask_id UUID REFERENCES subtasks(id) ON DELETE CASCADE,
    title TEXT NOT NULL,
    description TEXT,
    status task_status DEFAULT 'backlog',
    assignee_id UUID REFERENCES users(id),
    estimated_minutes INTEGER,
    actual_minutes INTEGER DEFAULT 0,
    due_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
    deleted_at TIMESTAMP WITH TIME ZONE NULL
);
CREATE INDEX idx_subtasks_task ON subtasks(task_id);
CREATE INDEX idx_subtasks_parent ON subtasks(parent_subtask_id);

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

-- ========== 注释/讨论 ==========
CREATE TABLE comments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    resource_type TEXT NOT NULL, -- 'task','project','subtask','file' 等
    resource_id UUID NOT NULL,
    user_id UUID REFERENCES users(id),
    content TEXT NOT NULL,
    content_html TEXT, -- 可选渲染版
    reply_to_comment_id UUID REFERENCES comments(id) ON DELETE SET NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
    deleted_at TIMESTAMP WITH TIME ZONE NULL
);
CREATE INDEX idx_comments_resource ON comments(resource_type, resource_id);

-- ========== 附件/文件 ==========
CREATE TABLE attachments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    owner_user_id UUID REFERENCES users(id),
    attached_to_type TEXT, -- 'task','comment','project','user'...
    attached_to_id UUID,
    file_name TEXT NOT NULL,
    file_size BIGINT,
    content_type TEXT,
    storage_key TEXT, -- 指向 S3 / 存储路径
    attachment_type attachment_type DEFAULT 'file',
    width INTEGER,
    height INTEGER,
    duration_seconds INTEGER,
    metadata JSONB DEFAULT '{}'::JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
    deleted_at TIMESTAMP WITH TIME ZONE NULL
);
CREATE INDEX idx_attachments_owner ON attachments(owner_user_id);
CREATE INDEX idx_attachments_resource ON attachments(attached_to_type, attached_to_id);

-- ========== 提醒/通知 ==========
CREATE TABLE reminders (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    task_id UUID REFERENCES tasks(id) ON DELETE CASCADE,
    remind_at TIMESTAMP WITH TIME ZONE NOT NULL,
    channel reminder_channel DEFAULT 'in_app',
    repeats recurrence_rule JSONB, -- 可选重复规则
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
    sent_at TIMESTAMP WITH TIME ZONE NULL
);
CREATE INDEX idx_reminders_user ON reminders(user_id);
CREATE INDEX idx_reminders_time ON reminders(remind_at);

CREATE TABLE notifications (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    level notification_level DEFAULT 'info',
    title TEXT,
    body TEXT,
    data JSONB,
    is_read BOOLEAN DEFAULT FALSE,
    channel reminder_channel DEFAULT 'in_app',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
    delivered_at TIMESTAMP WITH TIME ZONE NULL
);
CREATE INDEX idx_notifications_user ON notifications(user_id);
CREATE INDEX idx_notifications_read ON notifications(user_id, is_read);

-- ========== 日程 / 日历 集成 ==========
CREATE TABLE calendar_integrations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workspace_id UUID REFERENCES workspaces(id) ON DELETE CASCADE,
    user_id UUID REFERENCES users(id),
    provider oauth_provider,
    provider_account_id TEXT,
    access_token TEXT,
    refresh_token TEXT,
    token_expires_at TIMESTAMP WITH TIME ZONE,
    scope TEXT,
    config JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT now()
);

CREATE TABLE calendar_events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    integration_id UUID REFERENCES calendar_integrations(id) ON DELETE CASCADE,
    external_event_id TEXT,
    title TEXT,
    description TEXT,
    start_at TIMESTAMP WITH TIME ZONE,
    end_at TIMESTAMP WITH TIME ZONE,
    location TEXT,
    raw_event JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT now()
);

-- ========== AI 相关（任务分解/建议/对话/模型） ==========
CREATE TABLE ai_models (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL,
    kind ai_model_kind,
    provider TEXT, -- e.g., 'openai','internal'
    model_identifier TEXT, -- e.g., 'gpt-5-mini'
    config JSONB DEFAULT '{}'::JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT now()
);

CREATE TABLE ai_requests (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id),
    model_id UUID REFERENCES ai_models(id),
    prompt TEXT,
    prompt_tokens INTEGER,
    response JSONB, -- 原始响应
    response_text TEXT, -- 快速索引
    cost NUMERIC(12,6) DEFAULT 0,
    status TEXT DEFAULT 'completed',
    metadata JSONB DEFAULT '{}'::JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now()
);
CREATE INDEX idx_ai_requests_user ON ai_requests(user_id);

-- 存储 AI 给出的任务分解（结构化）
CREATE TABLE ai_task_suggestions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    ai_request_id UUID REFERENCES ai_requests(id) ON DELETE SET NULL,
    user_id UUID REFERENCES users(id),
    task_id UUID REFERENCES tasks(id) ON DELETE SET NULL,
    suggestion JSONB NOT NULL, -- 结构化分解树（可含子任务等）
    accepted BOOLEAN DEFAULT FALSE,
    rejected BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
    acted_at TIMESTAMP WITH TIME ZONE NULL
);
CREATE INDEX idx_ai_task_suggestions_user ON ai_task_suggestions(user_id);

-- AI 对话历史（如果支持对话式交互）
CREATE TABLE ai_chats (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id),
    title TEXT,
    metadata JSONB DEFAULT '{}'::JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT now()
);

CREATE TABLE ai_chat_messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    chat_id UUID REFERENCES ai_chats(id) ON DELETE CASCADE,
    role TEXT, -- 'user','assistant','system'
    content TEXT,
    content_json JSONB,
    model_id UUID REFERENCES ai_models(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now()
);

-- ========== 模板（任务模板、项目模板） ==========
CREATE TABLE task_templates (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workspace_id UUID REFERENCES workspaces(id) ON DELETE CASCADE,
    created_by UUID REFERENCES users(id),
    title TEXT NOT NULL,
    description TEXT,
    template_json JSONB NOT NULL, -- 存储一份任务结构化模板（含子任务/checklist）
    usage_count BIGINT DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT now()
);

CREATE TABLE project_templates (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workspace_id UUID REFERENCES workspaces(id) ON DELETE CASCADE,
    created_by UUID REFERENCES users(id),
    title TEXT NOT NULL,
    description TEXT,
    template_json JSONB NOT NULL,
    usage_count BIGINT DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT now()
);

-- ========== 智能列表 / 视图 / 过滤器 ==========
CREATE TABLE smart_lists (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workspace_id UUID REFERENCES workspaces(id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    query JSONB NOT NULL, -- 存储过滤器/排序规则
    created_by UUID REFERENCES users(id),
    is_shared BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT now()
);

-- ========== 习惯/目标（长期生命周期） ==========
CREATE TABLE goals (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workspace_id UUID REFERENCES workspaces(id) ON DELETE SET NULL,
    owner_id UUID REFERENCES users(id),
    title TEXT NOT NULL,
    description TEXT,
    start_date DATE,
    end_date DATE,
    progress NUMERIC(5,2) DEFAULT 0, -- 0-100
    metadata JSONB DEFAULT '{}'::JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
    deleted_at TIMESTAMP WITH TIME ZONE NULL
);

CREATE TABLE habits (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    title TEXT NOT NULL,
    schedule JSONB, -- e.g., {"days":["Mon","Wed"], "time":"08:00"}
    streak_count INTEGER DEFAULT 0,
    longest_streak INTEGER DEFAULT 0,
    metadata JSONB DEFAULT '{}'::JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT now()
);

-- ========== 时间追踪 / 番茄钟 ==========
CREATE TABLE time_entries (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id),
    task_id UUID REFERENCES tasks(id),
    subtask_id UUID REFERENCES subtasks(id),
    started_at TIMESTAMP WITH TIME ZONE NOT NULL,
    stopped_at TIMESTAMP WITH TIME ZONE,
    duration_seconds BIGINT,
    metadata JSONB DEFAULT '{}'::JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now()
);

CREATE TABLE pomodoro_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id),
    task_id UUID REFERENCES tasks(id),
    started_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
    ended_at TIMESTAMP WITH TIME ZONE,
    cycles INTEGER DEFAULT 0,
    metadata JSONB DEFAULT '{}'::JSONB
);

-- ========== 集成/OAuth/API Key/Webhook ==========
CREATE TABLE oauth_accounts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id),
    provider oauth_provider,
    provider_account_id TEXT,
    access_token TEXT,
    refresh_token TEXT,
    scope TEXT,
    expires_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now()
);

CREATE TABLE api_keys (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    label TEXT,
    key_hash TEXT NOT NULL, -- 存储 hash 而非明文
    revoked BOOLEAN DEFAULT FALSE,
    last_used_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now()
);

CREATE TABLE webhooks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workspace_id UUID REFERENCES workspaces(id) ON DELETE CASCADE,
    url TEXT NOT NULL,
    events TEXT[] DEFAULT ARRAY['task.created'],
    secret TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    last_failed_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now()
);

-- ========== 付费/订阅/发票 ==========
CREATE TABLE subscriptions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id UUID REFERENCES organizations(id) ON DELETE SET NULL,
    user_id UUID REFERENCES users(id) ON DELETE SET NULL,
    plan_id TEXT,
    status payment_status DEFAULT 'trial',
    starts_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
    ends_at TIMESTAMP WITH TIME ZONE,
    metadata JSONB DEFAULT '{}'::JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT now()
);

CREATE TABLE invoices (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    subscription_id UUID REFERENCES subscriptions(id) ON DELETE SET NULL,
    amount_cents BIGINT,
    currency TEXT,
    issued_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
    paid_at TIMESTAMP WITH TIME ZONE NULL,
    status TEXT,
    raw_invoice JSONB
);

-- ========== 审计 / 日志 / 事件 ==========
CREATE TABLE audit_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    actor_user_id UUID REFERENCES users(id),
    action TEXT NOT NULL,
    target_type TEXT,
    target_id UUID,
    details JSONB,
    ip_address INET,
    user_agent TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now()
);

CREATE TABLE usage_events (
    id BIGSERIAL PRIMARY KEY,
    user_id UUID REFERENCES users(id),
    event_type TEXT NOT NULL,
    event_properties JSONB,
    occurred_at TIMESTAMP WITH TIME ZONE DEFAULT now()
);
CREATE INDEX idx_usage_events_user ON usage_events(user_id);

-- ========== 系统配置/键值 ==========
CREATE TABLE system_settings (
    key TEXT PRIMARY KEY,
    value JSONB,
    description TEXT,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT now()
);

-- ========== 搜索索引与全文 ==========
-- 示例：对任务标题与描述启用全文检索字段（可在应用端做更新）
ALTER TABLE tasks ADD COLUMN IF NOT EXISTS tsv TSVECTOR;
CREATE INDEX IF NOT EXISTS idx_tasks_tsv ON tasks USING GIN (tsv);

-- 可创建触发器在插入/更新时填充 tsvector（此处仅示意，需要额外函数）
-- 例如：to_tsvector('chinese', coalesce(title,'') || ' ' || coalesce(description,''))

-- ========== 软删除辅助视图/表（可选） ==========
-- (略：按需实现)

-- ========== 示例触发器（更新时间） ==========
-- 自动更新 updated_at
CREATE OR REPLACE FUNCTION trigger_set_timestamp()
RETURNS TRIGGER AS $$
BEGIN
   NEW.updated_at = now();
   RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- 把触发器应用到常用表
CREATE TRIGGER trg_users_updated_at BEFORE UPDATE ON users
FOR EACH ROW EXECUTE FUNCTION trigger_set_timestamp();

CREATE TRIGGER trg_projects_updated_at BEFORE UPDATE ON projects
FOR EACH ROW EXECUTE FUNCTION trigger_set_timestamp();

CREATE TRIGGER trg_tasks_updated_at BEFORE UPDATE ON tasks
FOR EACH ROW EXECUTE FUNCTION trigger_set_timestamp();

-- ========== 权限与索引优化建议（注释） ==========
-- 建议对高并发日志表采用分区，对大 JSONB 字段建部分索引（GIN），对 time_entries、usage_events 做时间分区。
