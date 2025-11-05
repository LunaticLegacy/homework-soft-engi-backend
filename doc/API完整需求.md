# API通信需求

## 0. 基础请求体

Request示例：

```json
{
    "time": "当前时间戳",
    "token": "用户登录后的认证令牌，或null"
}
```

## 1. 用户机制

使用路由`/user`下的其他所有路由。

### 1.1 注册

`/user/register`，使用`POST`方法。

Request示例：

```json
{
    "time": "2025-11-05T10:00:00Z",
    "token": null,
    "username": "alice",
    "password": "password123",
    "email": "alice@example.com"
}
```
- 本Request中，`token`项必须为`null`。


Response示例:

```json
{
    "status": "success",
    "user_id": "uuid-string",
    "message": "注册成功"
}
```

### 1.2 登入

`/user/login`，使用`POST`方法。

Request示例：

```json
{
    "time": "2025-11-05T10:05:00Z",
    "token": null,
    "username": "alice",
    "password": "password123"
}
```
- 本Request中，`token`项必须为`null`。

Response示例：

```json
{
    "status": "success",
    "user_id": "uuid-string",
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "message": "登录成功"
}
```

### 1.3 登出

`/user/logout`，使用`POST`方法。

Request示例：
```json
{
    "time": "2025-11-05T10:10:00Z",
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```
- 本端口**必须**传入一个有效的token。

Response示例：

```json
{
    "status": "success",
    "message": "登出成功"
}
```

### 1.4 获取用户信息

`/user/profile/{user_id}`，使用`GET`方法。
- 其中，`{user_id}`为用户的ID。

Response示例：

```json
{
    "status": "success",
    "data": {
        "id": "uuid-string",
        "email": "alice@example.com",
        "full_name": "Alice Smith",
        "display_name": "Alice",
        "avatar_url": "https://example.com/avatar.jpg",
        "bio": "Software engineer",
        "job_title": "Developer",
        "organization": "Example Corp",
        "created_at": "2025-11-05T10:00:00Z"
    }
}
```

### 1.5 更新用户信息

`/user/profile/{user_id}`，使用`PUT`方法。

Request示例：

```json
{
    "time": "2025-11-05T10:15:00Z",
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "full_name": "Alice Johnson",
    "display_name": "AJ",
    "bio": "Senior software engineer"
}
```

Response示例：

```json
{
    "status": "success",
    "data": {
        "id": "uuid-string",
        "email": "alice@example.com",
        "full_name": "Alice Johnson",
        "display_name": "AJ",
        "bio": "Senior software engineer",
        "updated_at": "2025-11-05T10:15:00Z"
    },
    "message": "用户信息更新成功"
}
```

### 1.6 删除用户

`/user/profile/{user_id}`，使用`DELETE`方法。

Request示例：

```json
{
    "time": "2025-11-05T10:20:00Z",
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

Response示例：

```json
{
    "status": "success",
    "message": "用户删除成功"
}
```

## 2. 工作空间机制

使用路由`/workspaces`下的所有路由。

### 2.1 创建工作空间

`/workspaces`，使用`POST`方法。

Request示例：

```json
{
    "time": "2025-11-05T11:00:00Z",
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "name": "Project Alpha",
    "description": "Workspace for Project Alpha"
}
```

Response示例：

```json
{
    "status": "success",
    "data": {
        "id": "uuid-string",
        "name": "Project Alpha",
        "description": "Workspace for Project Alpha",
        "owner_user_id": "uuid-string",
        "created_at": "2025-11-05T11:00:00Z"
    },
    "message": "工作空间创建成功"
}
```

### 2.2 获取工作空间列表

`/workspaces`，使用`GET`方法。

Response示例：

```json
{
    "status": "success",
    "data": [
        {
            "id": "uuid-string",
            "name": "Project Alpha",
            "description": "Workspace for Project Alpha",
            "owner_user_id": "uuid-string",
            "created_at": "2025-11-05T11:00:00Z"
        }
    ],
    "count": 1
}
```

### 2.3 获取特定工作空间信息

`/workspaces/{workspace_id}`，使用`GET`方法。

Response示例：

```json
{
    "status": "success",
    "data": {
        "id": "uuid-string",
        "name": "Project Alpha",
        "description": "Workspace for Project Alpha",
        "owner_user_id": "uuid-string",
        "created_at": "2025-11-05T11:00:00Z",
        "updated_at": "2025-11-05T11:00:00Z"
    }
}
```

### 2.4 更新工作空间

`/workspaces/{workspace_id}`，使用`PUT`方法。

Request示例：

```json
{
    "time": "2025-11-05T11:05:00Z",
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "name": "Project Beta",
    "description": "Workspace for Project Beta"
}
```

Response示例：

```json
{
    "status": "success",
    "data": {
        "id": "uuid-string",
        "name": "Project Beta",
        "description": "Workspace for Project Beta",
        "owner_user_id": "uuid-string",
        "updated_at": "2025-11-05T11:05:00Z"
    },
    "message": "工作空间更新成功"
}
```

### 2.5 删除工作空间

`/workspaces/{workspace_id}`，使用`DELETE`方法。

Request示例：

```json
{
    "time": "2025-11-05T11:10:00Z",
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

Response示例：

```json
{
    "status": "success",
    "message": "工作空间删除成功"
}
```

## 3. 项目机制

使用路由`/projects`下的所有路由。

### 3.1 创建项目

`/projects`，使用`POST`方法。

Request示例：

```json
{
    "time": "2025-11-05T12:00:00Z",
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "workspace_id": "uuid-string",
    "title": "Website Redesign",
    "description": "Redesign company website"
}
```

Response示例：

```json
{
    "status": "success",
    "data": {
        "id": "uuid-string",
        "workspace_id": "uuid-string",
        "title": "Website Redesign",
        "description": "Redesign company website",
        "owner_id": "uuid-string",
        "created_at": "2025-11-05T12:00:00Z"
    },
    "message": "项目创建成功"
}
```

### 3.2 获取项目列表

`/projects`，使用`GET`方法。

可选查询参数：
- `workspace_id`: 工作空间ID
- `owner_id`: 所有者ID

Response示例：

```json
{
    "status": "success",
    "data": [
        {
            "id": "uuid-string",
            "workspace_id": "uuid-string",
            "title": "Website Redesign",
            "description": "Redesign company website",
            "owner_id": "uuid-string",
            "created_at": "2025-11-05T12:00:00Z"
        }
    ],
    "count": 1
}
```

### 3.3 获取特定项目信息

`/projects/{project_id}`，使用`GET`方法。

Response示例：

```json
{
    "status": "success",
    "data": {
        "id": "uuid-string",
        "workspace_id": "uuid-string",
        "title": "Website Redesign",
        "description": "Redesign company website",
        "owner_id": "uuid-string",
        "created_at": "2025-11-05T12:00:00Z",
        "updated_at": "2025-11-05T12:00:00Z"
    }
}
```

### 3.4 更新项目

`/projects/{project_id}`，使用`PUT`方法。

Request示例：

```json
{
    "time": "2025-11-05T12:05:00Z",
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "title": "Website Redesign Phase 1",
    "description": "Phase 1 of company website redesign"
}
```

Response示例：

```json
{
    "status": "success",
    "data": {
        "id": "uuid-string",
        "workspace_id": "uuid-string",
        "title": "Website Redesign Phase 1",
        "description": "Phase 1 of company website redesign",
        "owner_id": "uuid-string",
        "updated_at": "2025-11-05T12:05:00Z"
    },
    "message": "项目更新成功"
}
```

### 3.5 删除项目

`/projects/{project_id}`，使用`DELETE`方法。

Request示例：

```json
{
    "time": "2025-11-05T12:10:00Z",
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

Response示例：

```json
{
    "status": "success",
    "message": "项目删除成功"
}
```

## 4. 任务机制

使用路由`/tasks`下的所有路由。

### 4.1 创建任务

`/tasks`，使用`POST`方法。

Request示例：

```json
{
    "time": "2025-11-05T13:00:00Z",
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "project_id": "uuid-string",
    "title": "Design homepage layout",
    "description": "Create wireframes for homepage",
    "priority": "high",
    "due_at": "2025-11-15T10:00:00Z"
}
```

Response示例：

```json
{
    "status": "success",
    "data": {
        "id": "uuid-string",
        "project_id": "uuid-string",
        "title": "Design homepage layout",
        "description": "Create wireframes for homepage",
        "status": "backlog",
        "priority": "high",
        "due_at": "2025-11-15T10:00:00Z",
        "creator_id": "uuid-string",
        "created_at": "2025-11-05T13:00:00Z"
    },
    "message": "任务创建成功"
}
```

### 4.2 获取任务列表

`/tasks`，使用`GET`方法。

可选查询参数：
- `project_id`: 项目ID
- `assignee_id`: 分配给的用户ID
- `status`: 任务状态
- `workspace_id`: 工作空间ID

Response示例：

```json
{
    "status": "success",
    "data": [
        {
            "id": "uuid-string",
            "project_id": "uuid-string",
            "title": "Design homepage layout",
            "description": "Create wireframes for homepage",
            "status": "backlog",
            "priority": "high",
            "due_at": "2025-11-15T10:00:00Z",
            "creator_id": "uuid-string",
            "created_at": "2025-11-05T13:00:00Z"
        }
    ],
    "count": 1
}
```

### 4.3 获取特定任务信息

`/tasks/{task_id}`，使用`GET`方法。

Response示例：

```json
{
    "status": "success",
    "data": {
        "id": "uuid-string",
        "project_id": "uuid-string",
        "title": "Design homepage layout",
        "description": "Create wireframes for homepage",
        "status": "backlog",
        "priority": "high",
        "due_at": "2025-11-15T10:00:00Z",
        "creator_id": "uuid-string",
        "assignee_id": "uuid-string",
        "created_at": "2025-11-05T13:00:00Z",
        "updated_at": "2025-11-05T13:00:00Z"
    }
}
```

### 4.4 更新任务

`/tasks/{task_id}`，使用`PUT`方法。

Request示例：

```json
{
    "time": "2025-11-05T13:05:00Z",
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "title": "Design homepage layout and navigation",
    "status": "in_progress",
    "assignee_id": "uuid-string"
}
```

Response示例：

```json
{
    "status": "success",
    "data": {
        "id": "uuid-string",
        "project_id": "uuid-string",
        "title": "Design homepage layout and navigation",
        "description": "Create wireframes for homepage",
        "status": "in_progress",
        "priority": "high",
        "due_at": "2025-11-15T10:00:00Z",
        "creator_id": "uuid-string",
        "assignee_id": "uuid-string",
        "updated_at": "2025-11-05T13:05:00Z"
    },
    "message": "任务更新成功"
}
```

### 4.5 删除任务

`/tasks/{task_id}`，使用`DELETE`方法。

Request示例：

```json
{
    "time": "2025-11-05T13:10:00Z",
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

Response示例：

```json
{
    "status": "success",
    "message": "任务删除成功"
}
```

## 5. 标签机制

使用路由`/tags`下的所有路由。

### 5.1 创建标签

`/tags`，使用`POST`方法。

Request示例：

```json
{
    "time": "2025-11-05T14:00:00Z",
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "workspace_id": "uuid-string",
    "name": "Frontend",
    "color": "#FF0000"
}
```

Response示例：

```json
{
    "status": "success",
    "data": {
        "id": "uuid-string",
        "workspace_id": "uuid-string",
        "name": "Frontend",
        "color": "#FF0000",
        "created_by": "uuid-string",
        "created_at": "2025-11-05T14:00:00Z"
    },
    "message": "标签创建成功"
}
```

### 5.2 获取标签列表

`/tags`，使用`GET`方法。

可选查询参数：
- `workspace_id`: 工作空间ID

Response示例：

```json
{
    "status": "success",
    "data": [
        {
            "id": "uuid-string",
            "workspace_id": "uuid-string",
            "name": "Frontend",
            "color": "#FF0000",
            "created_by": "uuid-string",
            "created_at": "2025-11-05T14:00:00Z"
        }
    ],
    "count": 1
}
```

### 5.3 更新标签

`/tags/{tag_id}`，使用`PUT`方法。

Request示例：

```json
{
    "time": "2025-11-05T14:05:00Z",
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "name": "UI Design",
    "color": "#00FF00"
}
```

Response示例：

```json
{
    "status": "success",
    "data": {
        "id": "uuid-string",
        "workspace_id": "uuid-string",
        "name": "UI Design",
        "color": "#00FF00",
        "created_by": "uuid-string",
        "updated_at": "2025-11-05T14:05:00Z"
    },
    "message": "标签更新成功"
}
```

### 5.4 删除标签

`/tags/{tag_id}`，使用`DELETE`方法。

Request示例：

```json
{
    "time": "2025-11-05T14:10:00Z",
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

Response示例：

```json
{
    "status": "success",
    "message": "标签删除成功"
}
```

## 6. 评论机制

使用路由`/comments`下的所有路由。

### 6.1 创建评论

`/comments`，使用`POST`方法。

Request示例：

```json
{
    "time": "2025-11-05T15:00:00Z",
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "resource_type": "task",
    "resource_id": "uuid-string",
    "content": "This looks great! Can we add more details to the navigation?"
}
```

Response示例：

```json
{
    "status": "success",
    "data": {
        "id": "uuid-string",
        "resource_type": "task",
        "resource_id": "uuid-string",
        "user_id": "uuid-string",
        "content": "This looks great! Can we add more details to the navigation?",
        "created_at": "2025-11-05T15:00:00Z"
    },
    "message": "评论创建成功"
}
```

### 6.2 获取评论列表

`/comments`，使用`GET`方法。

必需查询参数：
- `resource_type`: 资源类型（task, project等）
- `resource_id`: 资源ID

Response示例：

```json
{
    "status": "success",
    "data": [
        {
            "id": "uuid-string",
            "resource_type": "task",
            "resource_id": "uuid-string",
            "user_id": "uuid-string",
            "content": "This looks great! Can we add more details to the navigation?",
            "created_at": "2025-11-05T15:00:00Z"
        }
    ],
    "count": 1
}
```

### 6.3 更新评论

`/comments/{comment_id}`，使用`PUT`方法。

Request示例：

```json
{
    "time": "2025-11-05T15:05:00Z",
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "content": "This looks great! Can we add more details to the navigation and footer?"
}
```

Response示例：

```json
{
    "status": "success",
    "data": {
        "id": "uuid-string",
        "resource_type": "task",
        "resource_id": "uuid-string",
        "user_id": "uuid-string",
        "content": "This looks great! Can we add more details to the navigation and footer?",
        "updated_at": "2025-11-05T15:05:00Z"
    },
    "message": "评论更新成功"
}
```

### 6.4 删除评论

`/comments/{comment_id}`，使用`DELETE`方法。

Request示例：

```json
{
    "time": "2025-11-05T15:10:00Z",
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

Response示例：

```json
{
    "status": "success",
    "message": "评论删除成功"
}
```

## 7. 附件机制

使用路由`/attachments`下的所有路由。

### 7.1 上传附件

`/attachments`，使用`POST`方法。

Request示例：

```json
{
    "time": "2025-11-05T16:00:00Z",
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "attached_to_type": "task",
    "attached_to_id": "uuid-string",
    "file_name": "design_mockup.png",
    "file_size": 1024000,
    "content_type": "image/png",
    "storage_key": "uploads/design_mockup.png"
}
```

Response示例：

```json
{
    "status": "success",
    "data": {
        "id": "uuid-string",
        "attached_to_type": "task",
        "attached_to_id": "uuid-string",
        "file_name": "design_mockup.png",
        "file_size": 1024000,
        "content_type": "image/png",
        "storage_key": "uploads/design_mockup.png",
        "owner_user_id": "uuid-string",
        "created_at": "2025-11-05T16:00:00Z"
    },
    "message": "附件上传成功"
}
```

### 7.2 获取附件列表

`/attachments`，使用`GET`方法。

可选查询参数：
- `attached_to_type`: 关联资源类型
- `attached_to_id`: 关联资源ID
- `owner_user_id`: 所有者ID

Response示例：

```json
{
    "status": "success",
    "data": [
        {
            "id": "uuid-string",
            "attached_to_type": "task",
            "attached_to_id": "uuid-string",
            "file_name": "design_mockup.png",
            "file_size": 1024000,
            "content_type": "image/png",
            "storage_key": "uploads/design_mockup.png",
            "owner_user_id": "uuid-string",
            "created_at": "2025-11-05T16:00:00Z"
        }
    ],
    "count": 1
}
```

### 7.3 删除附件

`/attachments/{attachment_id}`，使用`DELETE`方法。

Request示例：

```json
{
    "time": "2025-11-05T16:10:00Z",
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

Response示例：

```json
{
    "status": "success",
    "message": "附件删除成功"
}
```

## 8. 通知机制

使用路由`/notifications`下的所有路由。

### 8.1 获取通知列表

`/notifications`，使用`GET`方法。

可选查询参数：
- `is_read`: 是否已读

Response示例：

```json
{
    "status": "success",
    "data": [
        {
            "id": "uuid-string",
            "user_id": "uuid-string",
            "title": "Task assigned",
            "body": "You have been assigned to task 'Design homepage layout'",
            "level": "info",
            "is_read": false,
            "channel": "in_app",
            "created_at": "2025-11-05T17:00:00Z"
        }
    ],
    "count": 1
}
```

### 8.2 标记通知为已读

`/notifications/{notification_id}/read`，使用`PUT`方法。

Request示例：

```json
{
    "time": "2025-11-05T17:05:00Z",
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

Response示例：

```json
{
    "status": "success",
    "data": {
        "id": "uuid-string",
        "is_read": true,
        "delivered_at": "2025-11-05T17:05:00Z"
    },
    "message": "通知标记为已读"
}
```

### 8.3 删除通知

`/notifications/{notification_id}`，使用`DELETE`方法。

Request示例：

```json
{
    "time": "2025-11-05T17:10:00Z",
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

Response示例：

```json
{
    "status": "success",
    "message": "通知删除成功"
}
```

## 9. 搜索机制

使用路由`/search`下的所有路由。

### 9.1 搜索任务

`/search/tasks`，使用`GET`方法。

必需查询参数：
- `query`: 搜索关键词

Response示例：

```json
{
    "status": "success",
    "data": [
        {
            "id": "uuid-string",
            "title": "Design homepage layout",
            "description": "Create wireframes for homepage",
            "project_id": "uuid-string",
            "status": "in_progress"
        }
    ],
    "count": 1,
    "query": "homepage"
}
```

### 9.2 搜索项目

`/search/projects`，使用`GET`方法。

必需查询参数：
- `query`: 搜索关键词

Response示例：

```json
{
    "status": "success",
    "data": [
        {
            "id": "uuid-string",
            "title": "Website Redesign",
            "description": "Redesign company website",
            "workspace_id": "uuid-string"
        }
    ],
    "count": 1,
    "query": "website"
}
```

## 错误响应格式

所有错误响应遵循以下格式：

```json
{
    "status": "error",
    "error_code": "ERROR_CODE",
    "message": "错误描述信息",
    "details": {}
}
```

常见错误代码：
- `UNAUTHORIZED`: 未授权访问
- `NOT_FOUND`: 资源未找到
- `VALIDATION_ERROR`: 参数验证错误
- `INTERNAL_ERROR`: 内部服务器错误
- `DATABASE_ERROR`: 数据库错误
