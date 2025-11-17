-- AI Brand Studio Database Schema
-- For Phase 3 Cloud SQL (PostgreSQL) deployment

-- Sessions Table
-- Stores user session information
CREATE TABLE IF NOT EXISTS sessions (
    session_id VARCHAR(255) PRIMARY KEY,
    user_id VARCHAR(255) NOT NULL,
    application_id VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    metadata JSONB,
    CONSTRAINT sessions_user_id_idx CHECK (user_id IS NOT NULL)
);

CREATE INDEX IF NOT EXISTS idx_sessions_user_id ON sessions(user_id);
CREATE INDEX IF NOT EXISTS idx_sessions_created_at ON sessions(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_sessions_updated_at ON sessions(updated_at DESC);

-- Events Table
-- Stores all session events (messages, tool calls, etc.)
CREATE TABLE IF NOT EXISTS events (
    event_id SERIAL PRIMARY KEY,
    session_id VARCHAR(255) REFERENCES sessions(session_id) ON DELETE CASCADE,
    author VARCHAR(50) NOT NULL CHECK (author IN ('user', 'agent')),
    content TEXT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    event_type VARCHAR(50) NOT NULL, -- 'message', 'tool_call', 'generation', 'compaction'
    metadata JSONB
);

CREATE INDEX IF NOT EXISTS idx_events_session_id ON events(session_id);
CREATE INDEX IF NOT EXISTS idx_events_timestamp ON events(timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_events_type ON events(event_type);

-- Generated Brands Table
-- Stores all generated brand names for analytics and history
CREATE TABLE IF NOT EXISTS generated_brands (
    id SERIAL PRIMARY KEY,
    session_id VARCHAR(255) REFERENCES sessions(session_id) ON DELETE CASCADE,
    brand_name VARCHAR(255) NOT NULL,
    naming_strategy VARCHAR(50), -- 'portmanteau', 'descriptive', 'invented', 'acronym'
    rationale TEXT,
    tagline TEXT,
    syllables INTEGER,
    memorable_score INTEGER CHECK (memorable_score >= 0 AND memorable_score <= 10),

    -- Domain availability
    domain_com_available BOOLEAN,
    domain_ai_available BOOLEAN,
    domain_io_available BOOLEAN,

    -- Trademark info
    trademark_risk VARCHAR(20), -- 'low', 'medium', 'high', 'critical'
    trademark_conflicts INTEGER DEFAULT 0,

    -- SEO metrics
    seo_score INTEGER CHECK (seo_score >= 0 AND seo_score <= 100),
    meta_title TEXT,
    meta_description TEXT,

    -- Validation
    validation_status VARCHAR(20), -- 'clear', 'caution', 'blocked'
    validation_score INTEGER CHECK (validation_score >= 0 AND validation_score <= 100),

    -- User interaction
    user_selected BOOLEAN DEFAULT FALSE,
    user_rating INTEGER CHECK (user_rating >= 1 AND user_rating <= 5),

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    metadata JSONB
);

CREATE INDEX IF NOT EXISTS idx_brands_session_id ON generated_brands(session_id);
CREATE INDEX IF NOT EXISTS idx_brands_selected ON generated_brands(user_selected);
CREATE INDEX IF NOT EXISTS idx_brands_created_at ON generated_brands(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_brands_validation_status ON generated_brands(validation_status);
CREATE INDEX IF NOT EXISTS idx_brands_naming_strategy ON generated_brands(naming_strategy);

-- Brand Stories Table
-- Stores generated brand stories and marketing copy
CREATE TABLE IF NOT EXISTS brand_stories (
    id SERIAL PRIMARY KEY,
    brand_id INTEGER REFERENCES generated_brands(id) ON DELETE CASCADE,
    session_id VARCHAR(255) REFERENCES sessions(session_id) ON DELETE CASCADE,

    -- Story content
    brand_story TEXT,
    hero_copy TEXT,
    value_proposition TEXT,
    taglines JSONB, -- Array of tagline options

    -- SEO content
    primary_keywords JSONB,
    secondary_keywords JSONB,
    content_opportunities JSONB,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    metadata JSONB
);

CREATE INDEX IF NOT EXISTS idx_stories_brand_id ON brand_stories(brand_id);
CREATE INDEX IF NOT EXISTS idx_stories_session_id ON brand_stories(session_id);

-- User Preferences Table
-- Stores user preferences for personalization (Memory Bank alternative)
CREATE TABLE IF NOT EXISTS user_preferences (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(255) NOT NULL,
    preference_key VARCHAR(100) NOT NULL,
    preference_value JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, preference_key)
);

CREATE INDEX IF NOT EXISTS idx_preferences_user_id ON user_preferences(user_id);
CREATE INDEX IF NOT EXISTS idx_preferences_key ON user_preferences(preference_key);

-- Analytics View
-- Aggregated analytics for brand generation patterns
CREATE OR REPLACE VIEW brand_analytics AS
SELECT
    naming_strategy,
    validation_status,
    COUNT(*) as total_generated,
    AVG(validation_score) as avg_validation_score,
    AVG(seo_score) as avg_seo_score,
    SUM(CASE WHEN user_selected THEN 1 ELSE 0 END) as times_selected,
    AVG(user_rating) as avg_user_rating
FROM generated_brands
GROUP BY naming_strategy, validation_status;

-- Session Analytics View
-- Session activity metrics
CREATE OR REPLACE VIEW session_analytics AS
SELECT
    s.session_id,
    s.user_id,
    s.created_at,
    COUNT(DISTINCT e.event_id) as total_events,
    COUNT(DISTINCT gb.id) as total_brands_generated,
    SUM(CASE WHEN gb.user_selected THEN 1 ELSE 0 END) as brands_selected
FROM sessions s
LEFT JOIN events e ON s.session_id = e.session_id
LEFT JOIN generated_brands gb ON s.session_id = gb.session_id
GROUP BY s.session_id, s.user_id, s.created_at;

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger for sessions table
CREATE TRIGGER update_sessions_updated_at
    BEFORE UPDATE ON sessions
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Trigger for user_preferences table
CREATE TRIGGER update_preferences_updated_at
    BEFORE UPDATE ON user_preferences
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Comments for documentation
COMMENT ON TABLE sessions IS 'User sessions for brand generation workflows';
COMMENT ON TABLE events IS 'Session events including messages, tool calls, and actions';
COMMENT ON TABLE generated_brands IS 'All generated brand names with validation and metrics';
COMMENT ON TABLE brand_stories IS 'Marketing copy and stories for validated brands';
COMMENT ON TABLE user_preferences IS 'User preferences for personalization';
COMMENT ON VIEW brand_analytics IS 'Aggregated analytics on brand generation patterns';
COMMENT ON VIEW session_analytics IS 'Session-level activity metrics';
