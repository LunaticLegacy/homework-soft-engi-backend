-- 开启扩展（需要超级权限）
CREATE EXTENSION IF NOT EXISTS pgcrypto; -- 用于 gen_random_uuid()

-- ========== 自定义 ENUM 类型 ==========
CREATE TYPE user_role AS ENUM ('user','admin','owner','guest','support');
CREATE TYPE task_status AS ENUM ('backlog','todo','in_progress','blocked','done','cancelled');
CREATE TYPE priority_level AS ENUM ('low','medium','high','critical');
CREATE TYPE reminder_channel AS ENUM ('email','push','sms','in_app');
CREATE TYPE recurrence_freq AS ENUM ('none','daily','weekly','monthly','yearly','custom');
CREATE TYPE attachment_type AS ENUM ('file','image','audio','video','document','other');
CREATE TYPE integration_kind AS ENUM ('google_calendar','outlook','notion','slack','github','custom');
CREATE TYPE payment_status AS ENUM ('trial','active','past_due','cancelled','expired');
CREATE TYPE oauth_provider AS ENUM ('google','apple','github','microsoft','custom');
CREATE TYPE notification_level AS ENUM ('info','warning','error','success');
CREATE TYPE ai_model_kind AS ENUM ('decomposer','planner','summarizer','reminder','chat','other');