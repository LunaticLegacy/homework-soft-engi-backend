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