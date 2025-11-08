-- 获取活跃会话
SELECT 
    s.id,
    s.user_id,
    s.device_info,
    s.ip_address,
    s.user_agent,
    s.created_at,
    s.last_active_at,
    s.expires_at
FROM sessions s
WHERE s.user_id = $1 AND s.revoked = false AND s.expires_at > NOW()
ORDER BY s.last_active_at DESC;

-- 获取特定会话详情
SELECT 
    id,
    user_id,
    device_info,
    ip_address,
    user_agent,
    created_at,
    last_active_at,
    expires_at,
    revoked
FROM sessions 
WHERE id = $1;

-- 获取过期会话
SELECT 
    id,
    user_id,
    created_at,
    expires_at
FROM sessions 
WHERE expires_at < NOW() AND revoked = false
LIMIT $1;

-- 获取用户的会话数量
SELECT COUNT(*) as session_count
FROM sessions 
WHERE user_id = $1 AND revoked = false AND expires_at > NOW();