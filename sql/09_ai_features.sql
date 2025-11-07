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