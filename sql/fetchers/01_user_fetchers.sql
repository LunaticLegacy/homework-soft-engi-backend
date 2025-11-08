-- 获取所有用户基本信息
SELECT 
    id,
    email,
    email_verified,
    display_name,
    role,
    created_at,
    updated_at
FROM users 
WHERE deleted_at IS NULL;

-- 根据邮箱获取用户信息
SELECT 
    id,
    email,
    email_verified,
    full_name,
    display_name,
    avatar_url,
    locale,
    timezone,
    role,
    created_at,
    updated_at
FROM users 
WHERE email = $1 AND deleted_at IS NULL;

-- 获取用户详细信息（包括资料）
SELECT 
    u.id,
    u.email,
    u.email_verified,
    u.full_name,
    u.display_name,
    u.avatar_url,
    u.locale,
    u.timezone,
    u.role,
    u.created_at,
    u.updated_at,
    up.bio,
    up.pronouns,
    up.job_title,
    up.organization,
    up.settings
FROM users u
LEFT JOIN user_profiles up ON u.id = up.user_id
WHERE u.id = $1 AND u.deleted_at IS NULL;

-- 获取所有管理员用户
SELECT 
    id,
    email,
    email_verified,
    display_name,
    created_at
FROM users 
WHERE role = 'admin' AND deleted_at IS NULL
ORDER BY created_at DESC;

-- 获取未验证邮箱的用户
SELECT 
    id,
    email,
    display_name,
    created_at
FROM users 
WHERE email_verified = false AND deleted_at IS NULL
ORDER BY created_at ASC;

-- 按显示名称搜索用户
SELECT 
    id,
    email,
    display_name,
    avatar_url
FROM users 
WHERE display_name ILIKE '%' || $1 || '%' AND deleted_at IS NULL
LIMIT $2 OFFSET $3;