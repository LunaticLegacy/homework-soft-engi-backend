# API 通信需求（基于数据库模式的完善版）

本文档基于仓库中的 SQL 模式撰写，覆盖常用资源的端点、请求/响应格式、认证要求与示例。旨在为前后端对接提供清晰契约。

## 0. 通用约定

- 基本请求体示例（所有端点均接收）：

```json
{
  "time": "2025-11-05T10:00:00Z",
  "token": null
}
```

- 认证：使用 Bearer Token（JWT 或长 token）在请求头传递：
  - Header: Authorization: Bearer <token>
  - 文档中标注为 "Auth: required" 的接口必须提供有效 token。
  - 注册/登录接口中的 body 中 `token` 字段应为 null（见下）。

- 标准响应封装（统一格式）：

```json
{
  "status": "success" | "error",
  "code": 200,
  "message": "提示信息",
  "data": { ... }
}
```

- 常见错误码：
  - 400: 请求参数错误/验证失败
  - 401: 未认证或 token 无效
  - 403: 无权限
  - 404: 资源不存在
  - 409: 资源冲突（如唯一性冲突）
  - 500: 服务器错误

## 1. 用户与认证 (/user)

说明：数据库中存在 `users`, `user_profiles`, `sessions`, `password_resets`, `email_verifications` 等表。下列接口对应常见操作。

### 1.1 注册
- 路径：POST /user/register
- Auth：不需要（body 中 token 必须为 null）
- 请求体：

```json
{
  "time": "2025-11-05T10:00:00Z",
  "token": null,
  "email": "alice@example.com",
  "password": "password123",
  "full_name": "Alice",
  "display_name": "alice",
  "locale": "zh-CN"
}
```
- 验证规则：email 必填且唯一；password 最小长度（后端决定）；其他字段可选。
- 成功响应示例：

```json
{
  "status": "success",
  "code": 201,
  "message": "注册成功",
  "data": { "user_id": "<uuid>", "email_verified": false }
}
```

### 1.2 登录
- 路径：POST /user/login
- Auth：不需要（body 中 token 必须为 null）
- 请求体：

```json
{
  "time": "...",
  "token": null,
  "email": "alice@example.com",
  "password": "password123"
}
```
- 成功响应：返回 token 与 user_id

```json
{
  "status":"success",
  "code":200,
  "message":"登录成功",
  "data":{ "user_id":"<uuid>", "token":"<jwt token>", "expires_at":"..." }
}
```

### 1.3 登出
- 路径：POST /user/logout
- Auth：required
- 请求头：Authorization: Bearer <token>
- 请求体：{ "time": "..." }
- 操作：在 `sessions` 表中标记 session revoked 或删除 token
- 成功响应：status success

### 1.4 获取/更新个人资料
- 路径：GET /user/profile/{user_id}  (Auth: required; self or admin)
- 路径：PUT /user/profile/{user_id}  (Auth: required)
- GET 响应 data 示例：

```json
{
  "status":"success",
  "data":{
    "id":"<uuid>",
    "email":"alice@example.com",
    "full_name":"Alice",
    "display_name":"alice",
    "avatar_url":"...",
    "locale":"zh-CN",
    "role":"user",
    "profile":{ "bio":"...", "job_title":"..." }
  }
}
```

### 1.5 会话与 API Key
- GET /user/sessions (列出活跃 session) Auth required
- POST /user/sessions/revoke (撤销一个 session)
- API key 管理在 /integrations/api-keys（见后）

### 1.6 密码重置与邮箱验证
- POST /user/password-reset/request  (提供 email -> 生成 token 存入 password_resets)
- POST /user/password-reset/confirm  (token + new_password)
- POST /user/email/verify/request
- POST /user/email/verify/confirm (token)

## 2. 组织/工作区 (/orgs, /workspaces)

参考表：organizations, organization_members, workspaces, workspace_members

- POST /orgs            创建组织（Auth: required，role 限制）
- GET /orgs/{org_id}    组织详情
- PUT /orgs/{org_id}    更新组织设置
- POST /orgs/{org_id}/members  添加成员
- DELETE /orgs/{org_id}/members/{user_id}

- POST /workspaces      创建工作区（需指定 org 或为个人）
- GET /workspaces/{id}
- PUT /workspaces/{id}
- GET /workspaces/{id}/members
- POST /workspaces/{id}/members

所有创建类接口应返回新资源 id（UUID），并在请求体中校验必填项（如 name）。

## 3. 项目与任务 (/projects, /tasks, /subtasks)

核心表：projects, tasks, subtasks, task_dependencies, task_activity_logs

### 3.1 项目
- POST /projects  创建（Auth required）
  - body: { workspace_id, title (required), description, start_date, due_date }
  - 返回 201 + { project_id }

- GET /projects/{id}
- PUT /projects/{id}
- DELETE /projects/{id} (软删：设置 deleted_at)

### 3.2 任务
- POST /tasks  创建
  - 必填: title; 可选: project_id, assignee_id, due_at, priority
  - 校验: project 存在且 workspace 对应

- GET /tasks/{id}
- PUT /tasks/{id} 更新（status、assignee、title、description、estimated_minutes 等）
- PATCH /tasks/{id}/status  只更新状态，记录到 task_activity_logs
- POST /tasks/{id}/assign  指派用户（记录日志）
- POST /tasks/{id}/tags  添加标签（body: tag_ids）
- DELETE /tasks/{id}/tags/{tag_id}

- GET /workspaces/{w}/tasks?status=todo&assignee=...  支持过滤、排序与分页

### 3.3 子任务
- POST /tasks/{task_id}/subtasks
- GET /subtasks/{id}
- PUT /subtasks/{id}
- 支持 parent_subtask_id 实现树形结构

### 3.4 任务依赖
- POST /tasks/{task_id}/dependencies  (body: depends_on_task_id)
- DELETE /tasks/{task_id}/dependencies/{dep_id}

### 3.5 活动日志
- GET /tasks/{task_id}/activity  返回 task_activity_logs，按时间倒序

## 4. 标签与自定义字段 (/tags, /custom-fields)

- POST /workspaces/{w}/tags  创建标签（name 必填，workspace 唯一）
- GET /workspaces/{w}/tags
- POST /workspaces/{w}/custom-fields  创建自定义字段
- POST /tasks/{task_id}/custom-field-values  设置值

注意：数据库对 (workspace_id, name) 强制唯一，创建时返回 409 冲突错误。

## 5. 评论与附件 (/comments, /attachments)

### 5.1 评论
- POST /comments  (body: resource_type, resource_id, content, reply_to_comment_id?)
- GET /{resource_type}/{resource_id}/comments
- PUT /comments/{id}
- DELETE /comments/{id} (软删)

### 5.2 附件
- POST /attachments  (multipart/form-data 或先上传到存储后记录 metadata)
  - body: owner_user_id, attached_to_type, attached_to_id, file_name, storage_key, content_type
- GET /attachments/{id}
- DELETE /attachments/{id}

附件表包含 storage_key 字段用于指向外部对象存储（S3 等）。

## 6. 提醒与通知 (/reminders, /notifications)

- POST /reminders  创建提醒（user_id, task_id, remind_at, channel）
- GET /users/{user_id}/reminders
- POST /notifications/mark-read  标记通知为已读

通知表支持 is_read、level、channel、data（JSON）字段。

## 7. 日历集成 (/calendar)

- POST /calendar/integrations  添加第三方日历（存 tokens 到 calendar_integrations）
- GET /calendar/integrations/{id}/events
- Webhook 回调需映射外部 event 到 calendar_events 表

注意：存取第三方 token 时，请妥善加密或限制权限。

## 8. AI 功能 (/ai)

基于 ai_models, ai_requests, ai_task_suggestions, ai_chats, ai_chat_messages

- GET /ai/models
- POST /ai/requests  (user 发起模型调用，保存 ai_requests)
- GET /ai/requests/{id}
- POST /ai/suggestions/{suggestion_id}/accept
- POST /ai/chats  创建聊天会话
- POST /ai/chats/{chat_id}/messages  发送消息

注意：保存成本（cost 字段）与原始响应（response JSONB）。

## 9. 模板与智能列表 (/templates, /smart-lists)

- POST /templates/task  创建任务模板（template_json 必填）
- POST /smart-lists  创建智能列表（query JSON）

## 10. 时间追踪 (/time-entries, /pomodoro)

- POST /time-entries  开始/停止时段（started_at, stopped_at）
- POST /pomodoro-sessions  记录番茄钟会话

## 11. 集成与支付 (/integrations, /api-keys, /webhooks, /subscriptions)

- POST /integrations/oauth/connect  第三方 OAuth 回调
- GET /integrations/api-keys
- POST /integrations/api-keys  新建 API Key（返回明文时仅显示一次）
- POST /webhooks  配置 webhook

订阅/发票：
- GET /subscriptions/{id}
- POST /subscriptions  创建或变更计划

## 12. 审计 / 使用事件 / 系统设置

- 所有关键操作应写入 audit_logs（actor_user_id, action, details）
- usage_events 用于埋点统计（不阻塞主流程）
- 系统设置通过 /admin/settings 管理（key/value JSON）

## 13. 搜索 (/search)

- POST /search  (body: { query, resource_types:["tasks","projects"], filters:{...}, page, per_page })
- 后端应使用 tasks.tsv 列与全文检索（GIN）实现高效检索

## 14. 错误处理与边界情况

- 唯一键冲突返回 409，body 包含冲突字段
- 验证失败 400，返回字段级错误数组
- 未认证 401，返回 standard error

## 15. 示例：任务创建端点合同（契约）

- POST /tasks
- Auth: required
- Request body:

```json
{
  "time":"...",
  "token":"<jwt>",
  "project_id":"<uuid|null>",
  "workspace_id":"<uuid>",
  "title":"实现用户注册",
  "description":"支持 email+password 注册流程",
  "assignee_id":"<uuid|null>",
  "status":"backlog",
  "priority":"medium",
  "due_at":"2025-12-01T12:00:00Z",
  "estimated_minutes":120
}
```

- Success response:

```json
{
  "status":"success",
  "code":201,
  "message":"任务创建成功",
  "data":{ "task_id":"<uuid>" }
}
```

## 16. 与 SQL 模式的一致性检查要点（从 schema 派生）

- 所有 NOT NULL / UNIQUE 字段在文档中应标明为必填或可能返回 409。示例：`projects.title` NOT NULL；`users.email` UNIQUE NOT NULL。
- 软删除（deleted_at）策略：DELETE 接口建议实现软删并标注返回 204 或 200。
- 事务与并发：对会修改计数或唯一约束（e.g., tag 创建、template usage_count）操作应在事务中完成以避免竞态。

## 17. 未决问题与建议（可选后续工作）

- 认证细节：推荐明确使用 JWT（包含 exp）或基于 sessions 的短 token，同时支持 refresh token 流程。
- 文件上传流程：建议采用“先上传到云存储，回调写入 attachments 表”的方案；API 返回 storage_key。
- 搜索策略：在写入/更新任务时填充 tsvector（触发器或应用层更新），并为大 JSONB 字段创建部分 GIN 索引以提升性能。
- 提供 OpenAPI/Swagger 文档以便前端自动生成客户端。

---

如需我把上面的每个端点生成更详细的 OpenAPI schema（paths、components、模型）或直接生成后端路由/DTO/校验器样板，我可以继续实现。
