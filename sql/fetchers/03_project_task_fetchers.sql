-- 获取用户的所有项目
SELECT 
    id,
    name,
    description,
    owner_id,
    is_archived,
    created_at,
    updated_at
FROM projects 
WHERE owner_id = $1 AND deleted_at IS NULL
ORDER BY created_at DESC;

-- 获取项目详情
SELECT 
    id,
    name,
    description,
    owner_id,
    is_archived,
    created_at,
    updated_at
FROM projects 
WHERE id = $1 AND deleted_at IS NULL;

-- 获取项目中的任务列表
SELECT 
    t.id,
    t.title,
    t.description,
    t.project_id,
    t.assignee_id,
    t.status,
    t.priority,
    t.due_date,
    t.created_at,
    t.updated_at
FROM tasks t
JOIN projects p ON t.project_id = p.id
WHERE p.id = $1 AND t.deleted_at IS NULL AND p.deleted_at IS NULL
ORDER BY t.created_at DESC;

-- 获取指定状态的任务
SELECT 
    id,
    title,
    description,
    project_id,
    assignee_id,
    status,
    priority,
    due_date,
    created_at
FROM tasks 
WHERE status = $1 AND deleted_at IS NULL
ORDER BY due_date ASC NULLS LAST, created_at DESC;

-- 获取分配给用户的所有任务
SELECT 
    t.id,
    t.title,
    t.description,
    t.project_id,
    t.status,
    t.priority,
    t.due_date,
    t.created_at,
    p.name as project_name
FROM tasks t
JOIN projects p ON t.project_id = p.id
WHERE t.assignee_id = $1 AND t.deleted_at IS NULL AND p.deleted_at IS NULL
ORDER BY t.due_date ASC NULLS LAST;

-- 获取逾期任务
SELECT 
    id,
    title,
    description,
    project_id,
    assignee_id,
    status,
    priority,
    due_date
FROM tasks 
WHERE due_date < NOW() AND status != 'done' AND deleted_at IS NULL
ORDER BY due_date ASC;

-- 获取任务详情
SELECT 
    id,
    title,
    description,
    project_id,
    assignee_id,
    status,
    priority,
    due_date,
    created_at,
    updated_at
FROM tasks 
WHERE id = $1 AND deleted_at IS NULL;