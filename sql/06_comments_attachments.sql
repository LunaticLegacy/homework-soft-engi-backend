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