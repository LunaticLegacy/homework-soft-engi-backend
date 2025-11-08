-- 插入测试数据
-- 管理员用户
INSERT INTO users (
    email, email_verified, password_hash, display_name, role
)
VALUES (
    'lunaticlegacy@163.com', 
    true,
    '023eebe0943afc953b4c4ca02ec2d3a035a4ca7170914f6f20150a83be867247', -- lunamoon
    'lunaticlegacy',
    'admin'
)
RETURNING id;

INSERT INTO user_profiles (
    user_id, bio, pronouns, job_title, organization
)
SELECT id, 'System administrator', 'They/Them', 'Admin', 'TaskFlow'
FROM users WHERE email = 'lunaticlegacy@163.com';

-- 普通测试用户
INSERT INTO users (
    email, email_verified, password_hash, display_name, role
)
VALUES (
    'test@example.com',
    true,
    '5e884898da28047151d0e56f8dc6292773603d0d6aabbdd62a11ef721d1542d8', -- password
    'testuser',
    'user'
)
RETURNING id;

INSERT INTO user_profiles (
    user_id, bio, pronouns, job_title, organization
)
SELECT id, 'Test user for unit tests', 'He/Him', 'Tester', 'TaskFlow QA'
FROM users WHERE email = 'test@example.com';

-- 另一个测试用户 - 未验证邮箱
INSERT INTO users (
    email, email_verified, password_hash, display_name, role
)
VALUES (
    'unverified@example.com',
    false,
    '5e884898da28047151d0e56f8dc6292773603d0d6aabbdd62a11ef721d1542d8', -- password
    'unverified_user',
    'user'
);

INSERT INTO user_profiles (
    user_id, bio, pronouns, job_title, organization
)
SELECT id, 'Unverified test user', 'She/Her', 'Tester', 'TaskFlow QA'
FROM users WHERE email = 'unverified@example.com';

-- 删除所有测试用例的函数
-- 注意：这应该只在测试环境中运行
/*
  要删除所有测试数据，请按以下顺序执行：
  1. 删除用户资料
  2. 删除用户
  
  示例删除命令：
  DELETE FROM user_profiles WHERE user_id IN (
    SELECT id FROM users WHERE email IN ('lunaticlegacy@163.com', 'test@example.com', 'unverified@example.com')
  );
  
  DELETE FROM users WHERE email IN ('lunaticlegacy@163.com', 'test@example.com', 'unverified@example.com');
*/