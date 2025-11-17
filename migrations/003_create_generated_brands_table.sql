-- Migration 003: Create generated_brands table

CREATE TABLE IF NOT EXISTS generated_brands (
    id SERIAL PRIMARY KEY,
    session_id VARCHAR(255) NOT NULL,
    brand_name VARCHAR(255) NOT NULL,
    tagline TEXT,
    story TEXT,
    domain_status JSONB,
    trademark_risk VARCHAR(20) CHECK (trademark_risk IN ('low', 'medium', 'high', 'unknown')),
    seo_score FLOAT CHECK (seo_score >= 0 AND seo_score <= 100),
    user_selected BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    metadata JSONB,
    CONSTRAINT fk_generated_brands_session
        FOREIGN KEY (session_id)
        REFERENCES sessions(session_id)
        ON DELETE CASCADE
);
