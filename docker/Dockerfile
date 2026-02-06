FROM postgres:15

# 设置环境变量
ENV POSTGRES_DB=postgres
ENV POSTGRES_USER=postgres
ENV POSTGRES_PASSWORD=lunamoon
ENV POSTGRES_PORT=1980

# 复制所有SQL文件到docker-entrypoint-initdb.d目录下
# 按数字顺序命名以确保正确的执行顺序
COPY ../sql/01_types.sql /docker-entrypoint-initdb.d/01_types.sql
COPY ../sql/02_users_auth.sql /docker-entrypoint-initdb.d/02_users_auth.sql
COPY ../sql/03_org_workspace.sql /docker-entrypoint-initdb.d/03_org_workspace.sql
COPY ../sql/04_projects_tasks.sql /docker-entrypoint-initdb.d/04_projects_tasks.sql
COPY ../sql/09_ai_features.sql /docker-entrypoint-initdb.d/09_ai_features.sql

CMD ["postgres"]