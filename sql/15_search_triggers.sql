-- ========== 搜索索引与全文 ==========
-- 示例：对任务标题与描述启用全文检索字段（可在应用端做更新）
ALTER TABLE tasks ADD COLUMN IF NOT EXISTS tsv TSVECTOR;
CREATE INDEX IF NOT EXISTS idx_tasks_tsv ON tasks USING GIN (tsv);

-- 可创建触发器在插入/更新时填充 tsvector（此处仅示意，需要额外函数）
-- 例如：to_tsvector('chinese', coalesce(title,'') || ' ' || coalesce(description,''))

-- ========== 示例触发器（更新时间） ==========
-- 自动更新 updated_at
CREATE OR REPLACE FUNCTION trigger_set_timestamp()
RETURNS TRIGGER AS $$
BEGIN
   NEW.updated_at = now();
   RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- 把触发器应用到常用表
CREATE TRIGGER trg_users_updated_at BEFORE UPDATE ON users
FOR EACH ROW EXECUTE FUNCTION trigger_set_timestamp();

CREATE TRIGGER trg_projects_updated_at BEFORE UPDATE ON projects
FOR EACH ROW EXECUTE FUNCTION trigger_set_timestamp();

CREATE TRIGGER trg_tasks_updated_at BEFORE UPDATE ON tasks
FOR EACH ROW EXECUTE FUNCTION trigger_set_timestamp();

-- ========== 权限与索引优化建议（注释） ==========
-- 建议对高并发日志表采用分区，对大 JSONB 字段建部分索引（GIN），对 time_entries、usage_events 做时间分区。