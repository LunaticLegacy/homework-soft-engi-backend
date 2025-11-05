FROM postgres:15

# 设置环境变量
ENV POSTGRES_DB=postgres
ENV POSTGRES_USER=postgres
ENV POSTGRES_PASSWORD=lunamoon
ENV POSTGRES_PORT=1980

# 复制所有SQL文件到docker-entrypoint-initdb.d目录下
# 按数字顺序命名以确保正确的执行顺序
COPY ./sql/01_types.sql /docker-entrypoint-initdb.d/01_types.sql
COPY ./sql/02_users_auth.sql /docker-entrypoint-initdb.d/02_users_auth.sql
COPY ./sql/03_org_workspace.sql /docker-entrypoint-initdb.d/03_org_workspace.sql
COPY ./sql/04_projects_tasks.sql /docker-entrypoint-initdb.d/04_projects_tasks.sql
COPY ./sql/05_tags_fields.sql /docker-entrypoint-initdb.d/05_tags_fields.sql
COPY ./sql/06_comments_attachments.sql /docker-entrypoint-initdb.d/06_comments_attachments.sql
COPY ./sql/07_reminders_notifications.sql /docker-entrypoint-initdb.d/07_reminders_notifications.sql
COPY ./sql/08_calendar_integration.sql /docker-entrypoint-initdb.d/08_calendar_integration.sql
COPY ./sql/09_ai_features.sql /docker-entrypoint-initdb.d/09_ai_features.sql
COPY ./sql/10_templates_smart_lists.sql /docker-entrypoint-initdb.d/10_templates_smart_lists.sql
COPY ./sql/11_habits_goals.sql /docker-entrypoint-initdb.d/11_habits_goals.sql
COPY ./sql/12_time_tracking.sql /docker-entrypoint-initdb.d/12_time_tracking.sql
COPY ./sql/13_integrations_payments.sql /docker-entrypoint-initdb.d/13_integrations_payments.sql
COPY ./sql/14_audit_system.sql /docker-entrypoint-initdb.d/14_audit_system.sql
COPY ./sql/15_search_triggers.sql /docker-entrypoint-initdb.d/15_search_triggers.sql

CMD ["postgres"]