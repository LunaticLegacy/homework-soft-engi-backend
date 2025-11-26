-- ========== 基础用户与认证 ==========
CREATE TABLE users (            -- 用户
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),  -- id
    email TEXT UNIQUE NOT NULL,                     -- email
    email_verified BOOLEAN DEFAULT FALSE,           -- 是否验证了email
    password_hash TEXT,                             -- 密码，可以是null
    full_name TEXT,                                 -- 全名
    display_name TEXT,                              -- 显示名
    avatar_url TEXT,                                -- 个人主页URL
    locale TEXT DEFAULT 'zh-CN',                    -- 所在地区
    timezone TEXT DEFAULT 'Asia/China',             -- 时间
    role user_role NOT NULL DEFAULT 'user',         -- 用户权限组
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),  -- 账号创建时间
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT now(),  -- 账号信息更新时间
    deleted_at TIMESTAMP WITH TIME ZONE NULL    -- 用户删除
);
CREATE INDEX idx_users_email ON users(email);   -- 加入一个新的索引

CREATE TABLE user_profiles (    -- 用户信息
    user_id UUID PRIMARY KEY REFERENCES users(id) ON DELETE CASCADE,    -- 用户ID，用于访问profile的外键
    bio TEXT,                                                           -- 性别？
    pronouns TEXT,                                                      -- 称呼
    job_title TEXT,                                                     -- 工作单位
    organization TEXT,                                                  -- 组织
    settings JSONB DEFAULT '{}'::JSONB, -- 自定义个人设置
    metadata JSONB DEFAULT '{}'::JSONB, -- 备用扩展
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),      -- 创建时间
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT now()       -- 修改时间
);

CREATE TABLE sessions (     -- 连接
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

CREATE TABLE password_resets (      -- 重置密码
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    token TEXT NOT NULL UNIQUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
    used BOOLEAN DEFAULT FALSE
);

CREATE TABLE email_verifications (      -- 邮箱验证
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    token TEXT NOT NULL UNIQUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
    used BOOLEAN DEFAULT FALSE
);
