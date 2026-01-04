-- AI对话元数据表
CREATE TABLE ai_conversations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID REFERENCES projects(id) ON DELETE SET NULL,
    workspace_id UUID REFERENCES workspaces(id) ON DELETE SET NULL,
    creator_id UUID REFERENCES users(id) ON DELETE SET NULL,
    previous_conversation_id UUID REFERENCES ai_conversations(id) ON DELETE SET NULL,
    model_name VARCHAR(100),  -- 使用的大模型名称，如 "qwen-max"。
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
    deleted_at TIMESTAMP WITH TIME ZONE NULL
);

-- 每一轮对话的内容
CREATE TABLE ai_messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    conversation_id UUID NOT NULL REFERENCES ai_conversations(id) ON DELETE CASCADE,
    role VARCHAR(20) NOT NULL CHECK (role IN ('user', 'assistant', 'system')),
    content TEXT NOT NULL,
    tokens INT DEFAULT 0,                -- 可选：用于计费或上下文长度控制
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
    sequence_number INT                  -- 可选：显式顺序号，避免依赖时间戳排序
);