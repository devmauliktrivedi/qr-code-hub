CREATE INDEX IF NOT EXISTS idx_sessions_token ON sessions(token);
CREATE INDEX IF NOT EXISTS idx_sessions_active ON sessions(user_id, logout_time);
CREATE INDEX IF NOT EXISTS idx_qr_codes_user_deleted ON qr_codes(user_id, deleted_at);
CREATE INDEX IF NOT EXISTS idx_comments_created_at ON comments(created_at);
