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