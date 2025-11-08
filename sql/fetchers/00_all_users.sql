-- 获取系统中所有用户（谨慎使用）
SELECT 
    id,
    email,
    email_verified,
    full_name,
    display_name,
    role,
    created_at,
    updated_at
FROM users 
WHERE deleted_at IS NULL
ORDER BY created_at DESC;