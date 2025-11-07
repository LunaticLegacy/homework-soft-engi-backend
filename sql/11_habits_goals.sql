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